from __future__ import annotations

import logging

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv

from .api import TOPdeskAPI
from .const import DEFAULT_UPDATE_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class TopdeskConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for TOPdesk."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        error_details = {}

        if user_input is not None:
            try:
                api = TOPdeskAPI(
                    user_input["host"],
                    user_input["username"],
                    user_input["app_password"],
                    user_input["instance_name"],
                )
                api.instance_name = user_input[
                    "instance_name"
                ]  # Sets the users instance name
                await api.test_connection()

                return self.async_create_entry(
                    title=user_input["instance_name"], data=user_input
                )
            except ValueError as e:
                error_msg = str(e)
                _LOGGER.error("Error in TOPdeskConfigFlow: %s", error_msg)
                if error_msg == "connection_error":
                    errors["base"] = "connection_error"
                    error_details["error_detail"] = error_msg
                elif error_msg == "http_error":
                    errors["base"] = "cannot_connect"
                    error_details["error_detail"] = error_msg
                else:
                    errors["base"] = "unknown_error"
                    error_details["error_detail"] = error_msg

        data_schema = vol.Schema(
            {
                vol.Required("instance_name"): str,
                vol.Required("host"): str,
                vol.Required("username"): str,
                vol.Required("app_password"): str,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )
        """
        errors = {}

        if user_input is not None:
            try:
                # Validatie logica hier
                return self.async_create_entry(
                    title=user_input["instance_name"],
                    data=user_input,
                    options={"update_interval": DEFAULT_UPDATE_INTERVAL},
                )
            except Exception as err:
                errors["base"] = "connection_error"

        data_schema = vol.Schema(
            {
                vol.Required("instance_name"): str,
                vol.Required("host"): str,
                vol.Required("username"): str,
                vol.Required("app_password"): str,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )
    """

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow."""
        return TopdeskOptionsFlowHandler(config_entry)


class TopdeskOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle TOPdesk options."""

    def __init__(self, config_entry):
        super().__init__()

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        errors = {}

        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options_schema = vol.Schema(
            {
                vol.Required(
                    "update_interval",
                    default=self.config_entry.options.get(
                        "update_interval", DEFAULT_UPDATE_INTERVAL
                    ),
                ): cv.positive_int
            }
        )

        return self.async_show_form(
            step_id="init", data_schema=options_schema, errors=errors
        )
