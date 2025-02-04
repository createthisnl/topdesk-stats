"""
Definitions for TOPdesk Statistics integration.

topdesk_stats/sensor.py
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.components.sensor import SensorEntityDescription, SensorStateClass

from .const import (
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
    from collections.abc import Callable


@dataclass(frozen=True)
class TOPdeskSensorEntityDescription(SensorEntityDescription):
    """Class describing TOPdesk sensor entities."""

    value_fn: Callable = lambda _: None
    available_fn: Callable = lambda _: True
    exists_fn: Callable = lambda _: True
    extra_attributes: Callable = lambda _: {}
    icon: str = "mdi:help-circle"


TOPDESK_INCIDENT_SENSORS: tuple[TOPdeskSensorEntityDescription, ...] = (
    TOPdeskSensorEntityDescription(
        key=SENSOR_INCIDENT_TOTAL_TICKETS,
        translation_key=SENSOR_INCIDENT_TOTAL_TICKETS,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:file-document-outline",
        value_fn=lambda self: self.coordinator.data.get(self.entity_description.key),
    ),
    TOPdeskSensorEntityDescription(
        key=SENSOR_INCIDENT_CLOSED_TICKETS,
        translation_key=SENSOR_INCIDENT_CLOSED_TICKETS,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:file-document-check-outline",
        value_fn=lambda self: self.coordinator.data.get(self.entity_description.key),
    ),
    TOPdeskSensorEntityDescription(
        key=SENSOR_INCIDENT_COMPLETED_TICKETS,
        translation_key=SENSOR_INCIDENT_COMPLETED_TICKETS,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:file-document-edit-outline",
        value_fn=lambda self: self.coordinator.data.get(self.entity_description.key),
    ),
    TOPdeskSensorEntityDescription(
        key=SENSOR_INCIDENT_COMPLETED_TODAY,
        translation_key=SENSOR_INCIDENT_COMPLETED_TODAY,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:file-document-check",
        value_fn=lambda self: self.coordinator.data.get(self.entity_description.key),
    ),
    TOPdeskSensorEntityDescription(
        key=SENSOR_INCIDENT_NEW_TODAY,
        translation_key=SENSOR_INCIDENT_NEW_TODAY,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:file-document-plus",
        value_fn=lambda self: self.coordinator.data.get(self.entity_description.key),
    ),
)

TOPDESK_CHANGE_SENSORS: tuple[TOPdeskSensorEntityDescription, ...] = (
    TOPdeskSensorEntityDescription(
        key=SENSOR_CHANGE_TOTAL_TICKETS,
        translation_key=SENSOR_CHANGE_TOTAL_TICKETS,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:file-document-outline",
        value_fn=lambda self: self.coordinator.data.get(self.entity_description.key),
    ),
    TOPdeskSensorEntityDescription(
        key=SENSOR_CHANGE_CLOSED_TICKETS,
        translation_key=SENSOR_CHANGE_CLOSED_TICKETS,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:file-document-check-outline",
        value_fn=lambda self: self.coordinator.data.get(self.entity_description.key),
    ),
    TOPdeskSensorEntityDescription(
        key=SENSOR_CHANGE_COMPLETED_TICKETS,
        translation_key=SENSOR_CHANGE_COMPLETED_TICKETS,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:file-document-edit-outline",
        value_fn=lambda self: self.coordinator.data.get(self.entity_description.key),
    ),
    TOPdeskSensorEntityDescription(
        key=SENSOR_CHANGE_COMPLETED_TODAY,
        translation_key=SENSOR_CHANGE_COMPLETED_TODAY,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:file-document-check",
        value_fn=lambda self: self.coordinator.data.get(self.entity_description.key),
    ),
    TOPdeskSensorEntityDescription(
        key=SENSOR_CHANGE_NEW_TODAY,
        translation_key=SENSOR_CHANGE_NEW_TODAY,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:file-document-plus",
        value_fn=lambda self: self.coordinator.data.get(self.entity_description.key),
    ),
)
