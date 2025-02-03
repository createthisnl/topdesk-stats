"""
Coordinator for TOPdesk Statistics integration.

topdesk_stats/coordinator.py
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import async_timeout
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    SENSOR_INCIDENT_CLOSED_TICKETS,
    SENSOR_INCIDENT_COMPLETED_TICKETS,
    SENSOR_INCIDENT_COMPLETED_TODAY,
    SENSOR_INCIDENT_NEW_TODAY,
)

if TYPE_CHECKING:
    from datetime import timedelta

    from homeassistant.core import HomeAssistant

    from .api import TOPdeskAPI

_LOGGER = logging.getLogger(__name__)


def raise_update_failed(msg: str) -> None:
    """Throw UpdateFailed exceptions in a neat way."""
    _LOGGER.error(msg)
    raise UpdateFailed(msg)


class TopdeskDataUpdateCoordinator(DataUpdateCoordinator):
    """Manages data updates for TOPdesk integration."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: TOPdeskAPI,
        update_interval: timedelta,
        config_entry_id: str,
    ) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=api.instance_name,
            update_interval=update_interval,
        )
        self.api = api
        self.device_id = api.device_id  # Unieke device ID
        self.config_entry_id = config_entry_id  # Config entry ID toegevoegd
        self.device_info = {
            "identifiers": {(DOMAIN, self.config_entry_id)},
            "name": api.instance_name,
            "manufacturer": "TOPdesk",
            "model": "Enterprise",
            "model_id": "SaaS",
            "sw_version": api.instance_version,  # De versie wordt hier al ingevuld
            "entry_type": DeviceEntryType.SERVICE,
            "configuration_url": api.host,
        }
        _LOGGER.info(
            "Initialized coordinator with update interval: %s", update_interval
        )

    async def _async_update_data(self) -> dict[str, int | None]:
        """Fetch data from API."""
        _LOGGER.debug("Starting async data update")

        try:
            async with async_timeout.timeout(15), self.api:
                # Get the version and update the api instance_version
                version = await self.api.fetch_version()
                if version:
                    self.api.instance_version = (
                        version  # Update de versie naar de juiste waarde
                    )
                else:
                    raise_update_failed("Failed to fetch version info.")

                # Update the device info in the Device Registry of Home Assistant
                device_registry = dr.async_get(self.hass)
                device_entry = device_registry.async_get_or_create(
                    config_entry_id=self.config_entry_id,
                    identifiers={(DOMAIN, self.config_entry_id)},
                    name=self.api.instance_name,
                    model="Enterprise",
                    sw_version=self.api.instance_version,
                    configuration_url=self.api.host,
                )
                _LOGGER.debug("Update device_registry: %s", device_entry)

                # Get the tickets
                data = await self.api.fetch_tickets()

                # Check for incomplete data
                if None in data:
                    raise_update_failed(f"Received incomplete data from API: {data}")

                _LOGGER.debug("Successfully received update data: %s", data)
                return {
                    SENSOR_INCIDENT_COMPLETED_TICKETS: data[0],
                    SENSOR_INCIDENT_CLOSED_TICKETS: data[1],
                    SENSOR_INCIDENT_NEW_TODAY: data[2],
                    SENSOR_INCIDENT_COMPLETED_TODAY: data[3],
                }

        except Exception as err:
            _LOGGER.exception("Data update failed:")
            msg = f"Error communicating with API: {err}"
            raise UpdateFailed(msg) from err
