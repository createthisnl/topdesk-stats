from __future__ import annotations

import logging
from datetime import timedelta

import async_timeout
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import TOPdeskAPI
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class TopdeskDataUpdateCoordinator(DataUpdateCoordinator):
    """Manages data updates for TOPdesk integration."""

    def __init__(
        self, hass: HomeAssistant, api: TOPdeskAPI, update_interval: timedelta
    ):
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=api.instance_name,
            update_interval=update_interval,
        )
        self.api = api
        self.device_id = api.device_id  # Unieke device ID
        self.device_info = {
            "identifiers": {(DOMAIN, api.device_id)},
            "name": api.instance_name,
            "manufacturer": "TOPdesk",
            "model": "Enterprise",
            "model_id": "SaaS",
            "sw_version": api.instance_version,
            "entry_type": DeviceEntryType.SERVICE,
            "configuration_url": api.host,
        }
        _LOGGER.info(
            "Initialized coordinator with update interval: %s", update_interval
        )

    async def _async_update_data(self):
        """Fetch data from API."""
        _LOGGER.debug("Starting data update")

        try:
            async with async_timeout.timeout(15):
                await self.api.fetch_version()
                data = await self.api.fetch_tickets()

                if None in data:
                    _LOGGER.error("Received incomplete data from API: %s", data)
                    raise UpdateFailed("Invalid API response")

                _LOGGER.debug("Successfully received update data: %s", data)
                return {
                    "incident_completed_tickets": data[0],
                    "incident_closed_completed_count": data[1],
                    "incident_new_tickets_today": data[2],
                    "incident_completed_tickets_today": data[3],
                }

        except Exception as err:
            _LOGGER.error("Data update failed: %s", str(err))
            raise UpdateFailed(f"Error communicating with API: {err}") from err

    async def async_request_refresh(self) -> None:
        _LOGGER.debug("Refresh request recieved!")
        await super().async_request_refresh()
