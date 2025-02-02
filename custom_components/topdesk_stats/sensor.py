from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.components.sensor.const import SensorStateClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up sensors through coordinator."""
    coordinator = hass.data[DOMAIN]["coordinators"][config_entry.entry_id]
    instance_name = config_entry.data["instance_name"]

    _LOGGER.info("Setting up sensors for TOPdesk instance: %s", instance_name)

    sensors = [
        TopdeskSensor(coordinator, "incident_completed_tickets", instance_name),
        TopdeskSensor(coordinator, "incident_closed_completed_count", instance_name),
        TopdeskSensor(coordinator, "incident_new_tickets_today", instance_name),
        TopdeskSensor(coordinator, "incident_completed_tickets_today", instance_name),
    ]

    async_add_entities(sensors)
    _LOGGER.debug("Added %d sensors for instance %s", len(sensors), instance_name)


class TopdeskSensor(CoordinatorEntity, SensorEntity):
    """Represents a TOPdesk sensor entity."""

    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator, sensor_type, instance_name):
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._instance_name = instance_name
        self._attr_device_info = coordinator.device_info
        self._attr_unique_id = f"{coordinator.api.instance_name.lower().replace(' ', '_')}_{coordinator.api.device_id}_{sensor_type}"
        self._attr_translation_key = sensor_type
        _LOGGER.debug("Initialized sensor: %s", self.unique_id)

    @property
    def native_value(self):
        """Return sensor value from coordinator data."""
        value = self.coordinator.data.get(self._sensor_type)
        _LOGGER.debug("Current value for %s: %s", self.unique_id, value)
        return value

    @property
    def available(self) -> bool:
        """Return availability based on last update success."""
        return self.coordinator.last_update_success

    @property
    def device_class(self):
        """Indicate which type of sensor it is, 'count' for ticket counting method."""
        return "count"

    @property
    def state_class(self):
        """These are graphable measurements."""
        return SensorStateClass.MEASUREMENT

    @property
    def suggested_display_precision(self):
        """Dont use decimals."""
        return 0

    async def async_added_to_hass(self):
        """Handle entity addition to Home Assistant."""
        await super().async_added_to_hass()
        _LOGGER.info("Sensor %s added to Home Assistant", self.unique_id)
