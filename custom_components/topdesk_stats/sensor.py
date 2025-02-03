"""
Sensors for TOPdesk Statistics integration.

topdesk_stats/sensor.py
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.components.sensor import SensorEntity
from homeassistant.components.sensor.const import SensorStateClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_INSTANCE_NAME,
    DOMAIN,
    SENSOR_INCIDENT_CLOSED_TICKETS,
    SENSOR_INCIDENT_COMPLETED_TICKETS,
    SENSOR_INCIDENT_COMPLETED_TODAY,
    SENSOR_INCIDENT_NEW_TODAY,
)

# from .definitions import TOPDESK_SENSORS, TOPdeskSensorEntityDescription

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities) -> None:
    """Set up sensors through coordinator."""
    coordinator = hass.data[DOMAIN]["coordinators"][config_entry.entry_id]
    instance_name = config_entry.data[CONF_INSTANCE_NAME]

    _LOGGER.info("Setting up sensors for TOPdesk instance: %s", instance_name)

    #    for sensor in TOPDESK_SENSORS:
    #        if sensor.exists_fn(coordinator):
    #            async_add_entities([TopdeskSensor(coordinator, sensor, instance_name)])
    #            _LOGGER.debug("Added sensor for instance %s", instance_name)

    sensors = [
        TopdeskSensor(coordinator, SENSOR_INCIDENT_COMPLETED_TICKETS, instance_name),
        TopdeskSensor(coordinator, SENSOR_INCIDENT_CLOSED_TICKETS, instance_name),
        TopdeskSensor(coordinator, SENSOR_INCIDENT_COMPLETED_TODAY, instance_name),
        TopdeskSensor(coordinator, SENSOR_INCIDENT_NEW_TODAY, instance_name),
    ]
    async_add_entities(sensors)
    _LOGGER.debug("Added %d sensors for instance %s", len(sensors), instance_name)


class TopdeskSensor(CoordinatorEntity, SensorEntity):
    """Represents a TOPdesk sensor entity."""

    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator,
        sensor_type,
        instance_name: ConfigEntry,
    ):
        """Initialize TOPdesk sensor entity."""
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._instance_name = instance_name
        self._attr_device_info = coordinator.device_info
        self._attr_unique_id = f"{coordinator.api.instance_name.lower().replace(' ', '_')}_{coordinator.api.device_id}_{sensor_type}"  # noqa: E501
        self._attr_translation_key = sensor_type
        _LOGGER.debug("Initialized sensor: %s", self.unique_id)

    @property
    def native_value(self) -> int | None:
        """Return sensor value from coordinator data."""
        value = self.coordinator.data.get(self._sensor_type)
        # value = self._sensor_type.value_fn(self)
        _LOGGER.debug("Current value for %s: %s", self.unique_id, value)
        return value

    @property
    def available(self) -> bool:
        """Return availability based on last update success."""
        return self.coordinator.last_update_success

    @property
    def device_class(self) -> str:
        """Indicate which type of sensor it is, 'count' for ticket counting method."""
        return "count"

    @property
    def state_class(self):
        """These are graphable measurements."""
        return SensorStateClass.MEASUREMENT

    @property
    def suggested_display_precision(self) -> int:
        """Don't use decimals."""
        return 0

    @property
    def icon(self) -> str | None:
        """Return icon."""
        # icon = self._sensor_type.icon
        return "mdi:file-document"

    async def async_added_to_hass(self) -> None:
        """Handle entity addition to Home Assistant."""
        await super().async_added_to_hass()
        _LOGGER.info("Sensor %s added to Home Assistant", self.unique_id)

    async def async_update(self) -> None:
        """Manually trigger a refresh of the data for the sensor."""
        await self.coordinator.async_request_refresh()  # Force data refresh
        _LOGGER.debug("Sensor %s updated", self.unique_id)
