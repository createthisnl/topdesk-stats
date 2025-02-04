"""
Constants for TOPdesk Statistics integration.

topdesk_stats/sensor.py
"""

from __future__ import annotations

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "topdesk_stats"
BRAND = "TOPdesk"
ATTRIBUTION = "Data provided by your own TOPdesk instance"

DEFAULT_UPDATE_INTERVAL = 5  # minutes

# API Endpoints for TOPdesk ODATA API
API_INCIDENT_TYPE = "Incident Management"
API_INCIDENT_BASE_PATH = "/services/reporting/v2/odata/Incidents/"
API_CHANGE_TYPE = "Change Management"
API_CHANGE_BASE_PATH = "/services/reporting/v2/odata/Changes/"

# Sensor ID's
SENSOR_INCIDENT_TOTAL_TICKETS = "incident_total_tickets"
SENSOR_INCIDENT_COMPLETED_TICKETS = "incident_completed_tickets"
SENSOR_INCIDENT_CLOSED_TICKETS = "incident_closed_completed_count"
SENSOR_INCIDENT_NEW_TODAY = "incident_new_tickets_today"
SENSOR_INCIDENT_COMPLETED_TODAY = "incident_completed_tickets_today"

SENSOR_CHANGE_TOTAL_TICKETS = "change_total_tickets"
SENSOR_CHANGE_COMPLETED_TICKETS = "change_completed_tickets"
SENSOR_CHANGE_CLOSED_TICKETS = "change_closed_completed_count"
SENSOR_CHANGE_NEW_TODAY = "change_new_tickets_today"
SENSOR_CHANGE_COMPLETED_TODAY = "change_completed_tickets_today"

# Status codes
STATUS_200 = 200
STATUS_400 = 400
STATUS_401 = 401
STATUS_403 = 403
STATUS_404 = 404
STATUS_500 = 500

# CONF
CONF_INSTANCE_NAME = "instance_name"
CONF_INSTANCE_HOST = "instance_host"
CONF_INSTANCE_USERNAME = "instance_username"
CONF_INSTANCE_PASSWORD = "instance_password"  # noqa: S105
CONF_UPDATE_INTERVAL = "update_interval"
CONF_ENABLE_INCIDENTS = "enable_incidents"
CONF_ENABLE_CHANGES = "enable_changes"
