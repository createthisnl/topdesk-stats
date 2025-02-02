from __future__ import annotations

import logging
from datetime import timedelta

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .api import TOPdeskAPI
from .const import DEFAULT_UPDATE_INTERVAL, DOMAIN
from .coordinator import TopdeskDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up integration from config entry."""
    hass.data.setdefault(DOMAIN, {"coordinators": {}, "service_registered": False})

    # Action registration (once)
    if not hass.data[DOMAIN]["service_registered"]:
        _LOGGER.debug("Registering service...")

        async def async_trigger_update(call: ServiceCall) -> None:
            """Handle service call."""
            instance_name = call.data.get("instance_name")
            _LOGGER.debug(
                "Manually refresh data for instance: %s",
                instance_name or "all instances",
            )

            _LOGGER.debug(
                "Available instances: %s",
                [
                    c.config_entry.data["instance_name"]
                    for c in hass.data[DOMAIN]["coordinators"].values()
                ],
            )

            if DOMAIN not in hass.data or "coordinators" not in hass.data[DOMAIN]:
                _LOGGER.error("No TOPdesk-coordinators found")
                return

            refreshed = False
            for entry_id in list(hass.data[DOMAIN]["coordinators"].keys()):
                coordinator = hass.data[DOMAIN]["coordinators"][entry_id]
                config_name = coordinator.config_entry.data.get(
                    "instance_name", "Unknown"
                )

                if instance_name and config_name != instance_name:
                    _LOGGER.debug("Skipping %s (name doesn't match)", config_name)
                    continue

                try:
                    _LOGGER.info("Manually refresh data from %s", config_name)
                    await coordinator.async_request_refresh()
                    refreshed = True
                except Exception as err:
                    _LOGGER.error("Refresh failed from %s: %s", config_name, err)

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
                schema=vol.Schema({vol.Optional("instance_name"): str}),
            )
            hass.data[DOMAIN]["service_registered"] = True
            _LOGGER.info("Service successfully registered")
        except Exception as e:
            _LOGGER.error("Service registration failed: %s", str(e))
            return False

    api = TOPdeskAPI(
        entry.data["host"],
        entry.data["username"],
        entry.data["app_password"],
        entry.data["instance_name"],
    )

    update_interval = timedelta(
        minutes=entry.options.get("update_interval", DEFAULT_UPDATE_INTERVAL)
    )
    coordinator = TopdeskDataUpdateCoordinator(hass, api, update_interval)

    await coordinator.async_config_entry_first_refresh()

    # Directe coordinator opslag
    hass.data[DOMAIN]["coordinators"][entry.entry_id] = coordinator

    # Moderne platform setup
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    return True


async def update_listener(hass: HomeAssistant, entry: ConfigEntry):
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Verwijder de integratie."""
    instance_name = "Unknown"

    if entry.entry_id in hass.data[DOMAIN]["coordinators"]:
        coordinator = hass.data[DOMAIN]["coordinators"][entry.entry_id]
        instance_name = coordinator.config_entry.data.get("instance_name", "Unknown")
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
