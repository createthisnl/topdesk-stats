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
    API_CHANGE_TYPE,
    API_INCIDENT_TYPE,
    DOMAIN,
    SENSOR_CHANGE_CLOSED_TICKETS,
    SENSOR_CHANGE_COMPLETED_TICKETS,
    SENSOR_CHANGE_COMPLETED_TODAY,
    SENSOR_CHANGE_NEW_TODAY,
    SENSOR_CHANGE_TOTAL_TICKETS,
    SENSOR_INCIDENT_CLOSED_TICKETS,
    SENSOR_INCIDENT_COMPLETED_TICKETS,
    SENSOR_INCIDENT_COMPLETED_TODAY,
    SENSOR_INCIDENT_NEW_TODAY,
    SENSOR_INCIDENT_TOTAL_TICKETS,
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


class TOPdeskDataUpdateCoordinator(DataUpdateCoordinator):
    """Manages data updates for TOPdesk integration."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: TOPdeskAPI,
        update_interval: timedelta,
        config_entry_id: str,
        api_type: str,  # eg. "incidents" of "changes"
    ) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"{api.instance_name} ({api_type.capitalize()})",
            update_interval=update_interval,
        )
        self.api = api
        self.api_type = api_type
        self.device_id = f"{api.device_id}_{api_type}"  # Unique device ID per API-type
        self.config_entry_id = config_entry_id

        self.device_info = {
            "identifiers": {(DOMAIN, self.device_id)},
            "name": f"{api.instance_name} {api_type.capitalize()}",
            "manufacturer": "TOPdesk",
            "model": f"{api_type.capitalize()}",
            "model_id": "SaaS",
            "sw_version": api.instance_version,
            "entry_type": DeviceEntryType.SERVICE,
            "configuration_url": api.host,
        }

        _LOGGER.info(
            "Initialized coordinator for %s with update interval: %s",
            api_type,
            update_interval,
        )

    async def _async_update_data(self) -> dict[str, int | None]:
        """Fetch data from API."""
        _LOGGER.debug("Starting async data update for %s", self.api_type)

        try:
            async with async_timeout.timeout(15), self.api:
                # Get the version and update the API instance_version
                version = await self.api.fetch_version()
                if version:
                    self.api.instance_version = version
                else:
                    raise_update_failed(
                        f"Failed to fetch version info for {self.api_type}."
                    )

                # Update the device info in Home Assistant's Device Registry
                device_registry = dr.async_get(self.hass)
                device_registry.async_get_or_create(
                    config_entry_id=self.config_entry_id,
                    identifiers={(DOMAIN, self.device_id)},
                    name=f"{self.api.instance_name} {self.api_type.capitalize()}",
                    model=f"{self.api_type.capitalize()}",
                    sw_version=self.api.instance_version,
                    configuration_url=self.api.host,
                )

                # Get data from the correct API
                data = await self.api.fetch_tickets()

                # Check for incomplete data
                if None in data:
                    raise_update_failed(
                        f"Received incomplete data from API ({self.api_type}): {data}"
                    )

                _LOGGER.debug(
                    "Successfully received update data for %s: %s using %s",
                    self.api_type,
                    data,
                    self.api.base_url,
                )

                # Return depending on the type of API
                if self.api_type == API_INCIDENT_TYPE:
                    return {
                        SENSOR_INCIDENT_TOTAL_TICKETS: data[0],
                        SENSOR_INCIDENT_COMPLETED_TICKETS: data[1],
                        SENSOR_INCIDENT_CLOSED_TICKETS: data[2],
                        SENSOR_INCIDENT_NEW_TODAY: data[3],
                        SENSOR_INCIDENT_COMPLETED_TODAY: data[4],
                    }

                if self.api_type == API_CHANGE_TYPE:
                    return {
                        SENSOR_CHANGE_TOTAL_TICKETS: data[0],
                        SENSOR_CHANGE_COMPLETED_TICKETS: data[1],
                        SENSOR_CHANGE_CLOSED_TICKETS: data[2],
                        SENSOR_CHANGE_NEW_TODAY: data[3],
                        SENSOR_CHANGE_COMPLETED_TODAY: data[4],
                    }

                _LOGGER.warning("Unknown API type: %s", self.api_type)
                return {}

        except Exception as err:
            _LOGGER.exception("Data update failed for %s:", self.api_type)
            msg = f"Error communicating with API ({self.api_type}): {err}"
            raise UpdateFailed(msg) from err
