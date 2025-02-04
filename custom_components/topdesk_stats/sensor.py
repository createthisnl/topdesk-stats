"""
Sensors for TOPdesk Statistics integration.

topdesk_stats/sensor.py
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.components.sensor import SensorEntity
from homeassistant.components.sensor.const import SensorStateClass
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .const import (
    API_CHANGE_TYPE,
    API_INCIDENT_TYPE,
    CONF_INSTANCE_NAME,
    DOMAIN,
)
from .definitions import (
    TOPDESK_CHANGE_SENSORS,
    TOPDESK_INCIDENT_SENSORS,
    TOPdeskSensorEntityDescription,
)

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import TOPdeskDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors through coordinator."""
    coordinators = hass.data[DOMAIN]["coordinators"][config_entry.entry_id]
    instance_name = config_entry.data[CONF_INSTANCE_NAME]

    entities = []

    # Setup incident sensors
    coordinator_incidents = coordinators[API_INCIDENT_TYPE]
    for description in TOPDESK_INCIDENT_SENSORS:
        if description.exists_fn(coordinator_incidents):
            entities.append(
                TOPdeskSensor(coordinator_incidents, description, instance_name)
            )
            _LOGGER.debug(
                "Added incident sensor %s for instance %s",
                description.key,
                instance_name,
            )

    # Setup change sensors
    coordinator_changes = coordinators[API_CHANGE_TYPE]
    for description in TOPDESK_CHANGE_SENSORS:
        if description.exists_fn(coordinator_changes):
            entities.append(
                TOPdeskSensor(coordinator_changes, description, instance_name)
            )
            _LOGGER.debug(
                "Added change sensor %s for instance %s",
                description.key,
                instance_name,
            )

    async_add_entities(entities)
    _LOGGER.debug("Added %d sensors for instance %s", len(entities), instance_name)


class TOPdeskSensor(CoordinatorEntity, SensorEntity):
    """Represents a TOPdesk sensor entity."""

    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: TOPdeskDataUpdateCoordinator,
        entity_description: TOPdeskSensorEntityDescription,
        instance_name: str,
    ) -> None:
        """Initialize TOPdesk sensor entity."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._instance_name = instance_name
        self._attr_device_info = getattr(coordinator, "device_info", None)
        self._attr_unique_id = f"{coordinator.api.instance_name.lower().replace(' ', '_')}_{coordinator.api.device_id}_{entity_description.key}"  # noqa: E501
        self._attr_translation_key = entity_description.key
        _LOGGER.debug("Initialized sensor: %s", self.unique_id)

    @property
    def native_value(self) -> int | None:
        """Return sensor value from coordinator data."""
        value_fn = getattr(self.entity_description, "value_fn", lambda _: None)
        value = value_fn(self)
        _LOGGER.debug("Current value for %s: %s", self.unique_id, value)
        return value

    @property
    def available(self) -> bool:
        """Return availability based on last update success."""
        return self.coordinator.last_update_success and getattr(
            self.entity_description, "available_fn", False
        )

    @property
    def device_class(self) -> str:
        """Return the device class."""
        return "count"

    @property
    def state_class(self) -> str:
        """Return the state class."""
        return SensorStateClass.MEASUREMENT

    @property
    def suggested_display_precision(self) -> int:
        """Return display precision."""
        return 0

    @property
    def icon(self) -> str:
        """Return the icon to use in the frontend."""
        return self.entity_description.icon or "mdi:file-document"

    @property
    def extra_state_attributes(self) -> dict:
        """Return entity specific state attributes."""
        extra_attributes = getattr(
            self.entity_description, "extra_attributes", lambda _: {}
        )
        return extra_attributes(self)

    async def async_added_to_hass(self) -> None:
        """Handle entity addition to Home Assistant."""
        await super().async_added_to_hass()
        _LOGGER.info("Sensor %s added to Home Assistant", self.unique_id)

    async def async_update(self) -> None:
        """Manually trigger a refresh of the data for the sensor."""
        await self.coordinator.async_request_refresh()
        _LOGGER.debug("Sensor %s updated", self.unique_id)
