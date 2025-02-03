"""
TOPdesk Statistics integration.

topdesk_stats/__init__.py.
"""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import TYPE_CHECKING

import voluptuous as vol
from homeassistant.helpers import config_validation as cv

from .api import TOPdeskAPI
from .const import (
    CONF_INSTANCE_HOST,
    CONF_INSTANCE_NAME,
    CONF_INSTANCE_PASSWORD,
    CONF_INSTANCE_USERNAME,
    CONF_UPDATE_INTERVAL,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
)
from .coordinator import TopdeskDataUpdateCoordinator

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant, ServiceCall

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up integration from config entry."""
    hass.data.setdefault(DOMAIN, {"coordinators": {}, "service_registered": False})

    # Action registration (once)
    if not hass.data[DOMAIN]["service_registered"]:
        _LOGGER.debug("Registering service...")

        available_instances = [
            c.config_entry.data[CONF_INSTANCE_NAME]
            for c in hass.data[DOMAIN]["coordinators"].values()
        ]

        async def async_trigger_update(call: ServiceCall) -> None:
            """Handle service call."""
            instance_name = call.data.get(CONF_INSTANCE_NAME)
            _LOGGER.debug(
                "Manually refresh data for instance: %s",
                instance_name or "all instances",
            )

            _LOGGER.debug("Available instances: %s", available_instances)

            if DOMAIN not in hass.data or "coordinators" not in hass.data[DOMAIN]:
                _LOGGER.error("No TOPdesk-coordinators found")
                return

            refreshed = False
            for entry_id in list(hass.data[DOMAIN]["coordinators"].keys()):
                coordinator = hass.data[DOMAIN]["coordinators"][entry_id]
                config_name = coordinator.config_entry.data.get(
                    CONF_INSTANCE_NAME, "Unknown"
                )

                if instance_name and config_name != instance_name:
                    _LOGGER.debug("Skipping %s (name doesn't match)", config_name)
                    continue

                try:
                    _LOGGER.info("Manually refresh data from %s", config_name)
                    await coordinator.async_request_refresh()
                    refreshed = True
                except Exception:
                    _LOGGER.exception("Refresh failed from %s:", config_name)

            if not refreshed:
                _LOGGER.warning(
                    "No matching instances found for: %s",
                    instance_name or "all",
                )

        try:
            hass.services.async_register(
                DOMAIN,
                "trigger_update",
                async_trigger_update,
                schema=vol.Schema(
                    {
                        vol.Optional(CONF_INSTANCE_NAME): cv.string,
                    }
                ),
            )
            hass.data[DOMAIN]["service_registered"] = True
            _LOGGER.info("Service successfully registered")
        except Exception:
            _LOGGER.exception("Service registration failed:")
            return False

    async with TOPdeskAPI(
        entry.data[CONF_INSTANCE_HOST],
        entry.data[CONF_INSTANCE_USERNAME],
        entry.data[CONF_INSTANCE_PASSWORD],
        entry.data[CONF_INSTANCE_NAME],
    ) as api:
        # Get version and tickets
        await api.fetch_version()
        await api.fetch_tickets()

    config_entry_id = entry.entry_id

    update_interval = timedelta(
        minutes=entry.options.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
    )

    # Create the coordinator and provide the config_entry_id
    coordinator = TopdeskDataUpdateCoordinator(
        hass, api, update_interval, config_entry_id
    )

    # Start the coordinator
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN]["coordinators"][entry.entry_id] = coordinator

    # Platform setup
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    return True


async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Delete the integration."""
    instance_name = "Unknown"

    if entry.entry_id in hass.data[DOMAIN]["coordinators"]:
        coordinator = hass.data[DOMAIN]["coordinators"][entry.entry_id]
        instance_name = coordinator.config_entry.data.get(CONF_INSTANCE_NAME, "Unknown")
        del hass.data[DOMAIN]["coordinators"][entry.entry_id]

    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])

    # Only delete action if there are no instances left
    if not hass.data[DOMAIN]["coordinators"]:
        hass.services.async_remove(DOMAIN, "trigger_update")
        hass.data[DOMAIN]["service_registered"] = False

    _LOGGER.info(
        "TOPdesk statistics integration for %s is removed.",
        instance_name,
    )

    return unload_ok
