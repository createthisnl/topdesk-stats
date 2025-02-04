"""
Entity for TOPdesk Statistics integration.

topdesk_stats/entity.py
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

if TYPE_CHECKING:
    from .coordinator import TOPdeskDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


class TOPdeskBaseEntity(CoordinatorEntity, SensorEntity):
    """Base entity for TOPdesk sensors."""

    def __init__(
        self, coordinator: TOPdeskDataUpdateCoordinator, entity_id: str, name: str
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_entity_id = entity_id
        self._attr_name = name
        _LOGGER.debug("DEBUG check for self._attr_entity_id: %s", self._attr_entity_id)
        _LOGGER.debug("DEBUG check for self._attr_name: %s", self._attr_name)

    @property
    def native_value(self) -> Any:
        """Return the current value of the sensor."""
        return self.coordinator.data.get(self.entity_id)
