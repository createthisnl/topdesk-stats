"""Constants for topdesk_stats."""

from __future__ import annotations

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "topdesk_stats"
ATTRIBUTION = "Data provided by your own TOPdesk instance"

DEFAULT_UPDATE_INTERVAL = 5  # minutes

# API Endpoints voor de ODATA API van TOPdesk
API_INCIDENT_BASE_PATH = "/services/reporting/v2/odata/Incidents/"
API_CHANGE_BASE_PATH = "/services/reporting/v2/odata/Changes/"

# Sensor ID's
SENSOR_INCIDENT_TOTAL_TICKETS = "total_tickets"
SENSOR_INCIDENT_COMPLETED_TICKETS = "incident_completed_tickets"
SENSOR_INCIDENT_CLOSED_TICKETS = "incident_closed_completed_count"
SENSOR_INCIDENT_NEW_TODAY = "incident_new_tickets_today"
SENSOR_INCIDENT_COMPLETED_TODAY = "incident_completed_tickets_today"

# Binary Sensor ID's
BINARY_SENSOR_ACTIVE_INCIDENTS = "active_incidents"
BINARY_SENSOR_CRITICAL_INCIDENTS = "critical_incidents"
