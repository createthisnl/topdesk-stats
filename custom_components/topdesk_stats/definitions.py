"""
Definitions for TOPdesk Statistics integration.

topdesk_stats/sensor.py
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    EntityCategory,
    UnitOfLength,
    UnitOfMass,
    UnitOfTemperature,
    UnitOfTime,
)

from .const import (
    DOMAIN,
    SENSOR_INCIDENT_CLOSED_TICKETS,
    SENSOR_INCIDENT_COMPLETED_TICKETS,
    SENSOR_INCIDENT_COMPLETED_TODAY,
    SENSOR_INCIDENT_NEW_TODAY,
)

if TYPE_CHECKING:
    from collections.abc import Callable
    from datetime import datetime


@dataclass
class TOPdeskSensorEntityDescriptionMixin:
    """Mixin for required keys."""

    value_fn: Callable[..., Any]


@dataclass
class TOPdeskSensorEntityDescription(
    SensorEntityDescription, TOPdeskSensorEntityDescriptionMixin
):
    """Sensor entity description for Bambu Lab."""

    available_fn: Callable[..., bool] = lambda _: True
    exists_fn: Callable[..., bool] = lambda _: True
    extra_attributes: Callable[..., dict] = lambda _: {}
    # icon_fn: Callable[..., str] = lambda _: ""


TOPDESK_SENSORS: tuple[TOPdeskSensorEntityDescription, ...] = (
    TOPdeskSensorEntityDescription(
        key=SENSOR_INCIDENT_CLOSED_TICKETS,
        translation_key=SENSOR_INCIDENT_CLOSED_TICKETS,
        # native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        # device_class=SensorDeviceClass.?,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:file-document-check-outline",
        value_fn=lambda self: self.coordinator.data.get(self._sensor_type),
        # exists_fn=lambda coordinator: coordinator.get_model().supports_feature(something),
    ),
    TOPdeskSensorEntityDescription(
        key=SENSOR_INCIDENT_COMPLETED_TICKETS,
        translation_key=SENSOR_INCIDENT_COMPLETED_TICKETS,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:file-document-edit-outline",
        value_fn=lambda self: self.coordinator.data.get(self._sensor_type),
        # exists_fn=lambda coordinator: coordinator.get_model().supports_feature(something),
    ),
    TOPdeskSensorEntityDescription(
        key=SENSOR_INCIDENT_COMPLETED_TODAY,
        translation_key=SENSOR_INCIDENT_COMPLETED_TODAY,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:file-document-check",
        value_fn=lambda self: self.coordinator.data.get(self._sensor_type),
        # exists_fn=lambda coordinator: coordinator.get_model().supports_feature(something),
    ),
    TOPdeskSensorEntityDescription(
        key=SENSOR_INCIDENT_NEW_TODAY,
        translation_key=SENSOR_INCIDENT_NEW_TODAY,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:file-document-plus",
        value_fn=lambda self: self.coordinator.data.get(self._sensor_type),
        # exists_fn=lambda coordinator: coordinator.get_model().supports_feature(something),
    ),
)
