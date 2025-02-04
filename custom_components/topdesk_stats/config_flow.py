"""
Config flow for TOPdesk Statistics integration.

topdesk_stats/config_flow.py
"""

from __future__ import annotations

import logging
from typing import Any
from urllib.parse import urlparse

import voluptuous as vol
from aiohttp import InvalidURL
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv

from .api import TOPdeskAPI
from .const import (
    CONF_ENABLE_CHANGES,
    CONF_ENABLE_INCIDENTS,
    CONF_INSTANCE_HOST,
    CONF_INSTANCE_NAME,
    CONF_INSTANCE_PASSWORD,
    CONF_INSTANCE_USERNAME,
    CONF_UPDATE_INTERVAL,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
)

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_INSTANCE_NAME): cv.string,
        vol.Required(CONF_INSTANCE_HOST): cv.string,
        vol.Required(CONF_INSTANCE_USERNAME, default=""): cv.string,
        vol.Required(CONF_INSTANCE_PASSWORD, default=""): cv.string,
        vol.Optional(CONF_ENABLE_INCIDENTS, default=True): bool,
        vol.Optional(CONF_ENABLE_CHANGES, default=True): bool,
    }
)

_LOGGER = logging.getLogger(__name__)


class TOPdeskConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for TOPdesk."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> Any:
        """Handle the initial step."""
        errors = {}
        error_details = {}

        if user_input is not None:
            try:
                # Perform validation
                if not self._validate_host(user_input.get(CONF_INSTANCE_HOST)):
                    errors["host"] = "invalid_url"
                    msg = "Invalid URL: missing http:// of https://"
                    raise InvalidURL(msg)  # noqa: TRY301

                # Test de verbinding
                async with TOPdeskAPI(
                    user_input[CONF_INSTANCE_HOST],
                    user_input[CONF_INSTANCE_USERNAME],
                    user_input[CONF_INSTANCE_PASSWORD],
                    user_input[CONF_INSTANCE_NAME],
                ) as api:
                    if not await api.test_connection():
                        msg = "Conf_flow connection test failed"
                        raise ConnectionError(msg)  # noqa: TRY301

                return self.async_create_entry(
                    title=user_input["instance_name"], data=user_input
                )

            except InvalidURL as e:
                _LOGGER.exception("URL validation failed:")
                errors["base"] = "error_occured"
                error_details["error_detail"] = str(e)
            except ConnectionError as e:
                _LOGGER.exception("Connection error:")
                errors["base"] = "connection_error"
                error_details["error_detail"] = str(e)
            except Exception as e:
                _LOGGER.exception("Unexpected error during configuration:")
                errors["base"] = "unknown_error"
                error_details["error_detail"] = str(e)

        data_schema = DATA_SCHEMA

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders=error_details,
        )

    def _validate_host(self, host: Any) -> Any:
        """Validate the hostname format."""
        parsed_url = urlparse(host)
        return parsed_url.scheme or parsed_url.netloc

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> TOPdeskOptionsFlowHandler:
        """Get the options flow."""
        return TOPdeskOptionsFlowHandler(config_entry)


class TOPdeskOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle TOPdesk options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize TOPdesk options flow."""
        super().__init__()
        _LOGGER.debug("DEBUG check for config_entry: %s", config_entry)

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> Any:
        """Manage the options."""
        errors = {}

        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Get the update_interval from the configuration, with fallback to the default
        options_schema = vol.Schema(
            {
                # fix this # vol.Optional(
                # fix this #     CONF_INSTANCE_USERNAME,
                # fix this #     default=self.config_entry.options.get(
                # fix this #         CONF_INSTANCE_USERNAME, CONF_INSTANCE_USERNAME
                # fix this #     ),
                # fix this # ): cv.string,
                # fix this # vol.Optional(
                # fix this #     CONF_INSTANCE_PASSWORD,
                # fix this #     default=self.config_entry.options.get(
                # fix this #         CONF_INSTANCE_PASSWORD, CONF_INSTANCE_PASSWORD
                # fix this #     ),
                # fix this # ): cv.string,
                # fix this # vol.Optional(
                # fix this #     CONF_INSTANCE_HOST,
                # fix this #     default=self.config_entry.options.get(
                # fix this #         CONF_INSTANCE_HOST, "DEFAULT_INSTANCE_HOST"
                # fix this #     ),
                # fix this # ): cv.string,
                vol.Required(
                    CONF_UPDATE_INTERVAL,
                    default=self.config_entry.options.get(
                        CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL
                    ),
                ): cv.positive_int,
                vol.Optional(
                    CONF_ENABLE_INCIDENTS,
                    default=self.config_entry.options.get(CONF_ENABLE_INCIDENTS, True),
                ): bool,
                vol.Optional(
                    CONF_ENABLE_CHANGES,
                    default=self.config_entry.options.get(CONF_ENABLE_CHANGES, True),
                ): bool,
            }
        )

        return self.async_show_form(
            step_id="init", data_schema=options_schema, errors=errors
        )
