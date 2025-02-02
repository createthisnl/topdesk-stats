from __future__ import annotations
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import SensorEntity


class TOPdeskBaseEntity(CoordinatorEntity, SensorEntity):
    """Base entity for TOPdesk sensors."""

    def __init__(self, coordinator, entity_id, name):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_entity_id = (
            entity_id  # Gebruik _attr_entity_id in plaats van self.entity_id
        )
        self._attr_name = name

    @property
    def native_value(self):
        """Return the current value of the sensor."""
        return self.coordinator.data.get(self.entity_id)
