from __future__ import annotations

import base64
import hashlib
import logging
import urllib.parse
from datetime import datetime, timezone
from typing import Optional

import aiohttp
import pytz
from aiohttp import ClientError, ClientTimeout
from homeassistant.helpers import device_registry as dr
from .const import API_INCIDENT_BASE_PATH

_LOGGER = logging.getLogger(__name__)


class TOPdeskAPI:
    """Handles communication with the TOPdesk API."""

    def __init__(self, host: str, username: str, app_password: str, instance_name: str):
        self.instance_name = instance_name  # Set via config_flow
        self.instance_version = ""  # needs to be set by self.fetch_version() or so.
        self.device_id = hashlib.md5(host.encode()).hexdigest()[:10]
        self.host = host.rstrip("/")
        self.base_url = f"{self.host}" + API_INCIDENT_BASE_PATH
        self.auth_header = base64.b64encode(
            f"{username}:{app_password}".encode()
        ).decode()
        self.timeout = ClientTimeout(total=15)
        self.session = aiohttp.ClientSession()
        _LOGGER.debug("Initialized TOPdeskAPI for %s", self.host)

    def _generate_device_id(self) -> str:
        """Generate a unique device ID based on hostname."""
        return hashlib.md5(self.host.encode()).hexdigest()[:10]

    async def fetch_version(self) -> Optional[str]:
        """Fetch the product version."""
        try:
            async with aiohttp.ClientSession() as session:
                return await self._fetch_product_version(session)
        except Exception as err:
            _LOGGER.error("Error fetching version: %s", err)
            return None

    async def test_connection(self) -> bool:
        """Test API connectivity."""
        try:
            await self.fetch_tickets()
            return True
        except Exception:
            return False

    async def fetch_tickets(self):
        """Fetch ticket counts using OData queries."""
        try:
            async with aiohttp.ClientSession() as session:
                completed_count = await self._fetch_count(
                    session, "(completed eq true)"
                )
                closed_completed_count = await self._fetch_count(
                    session, "(completed eq true) and (closed eq true)"
                )
                new_today_count = await self._fetch_new_today_count(session)
                completed_today_count = await self._fetch_completed_today_count(session)
                return (
                    completed_count,
                    closed_completed_count,
                    new_today_count,
                    completed_today_count,
                )
        except Exception as err:
            _LOGGER.error("API error: %s", err)
            return None, None, None, None

    async def _fetch_new_today_count(self, session):
        """Fetch new tickets created today."""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%dT00:00:00Z")
        filter_query = f"(creationDate ge {today})"
        return await self._fetch_count(session, filter_query)

    async def _fetch_completed_today_count(self, session):
        """Fetch new tickets created today."""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%dT00:00:00Z")
        filter_query = (
            f"(creationDate ge {today}) and (completed eq true) and (closed eq false)"
        )
        return await self._fetch_count(session, filter_query)

    async def _fetch_count(self, session, filter_query: str) -> Optional[int]:
        """Fetch count using original working method."""
        try:
            encoded_filter = urllib.parse.quote(filter_query)
            url = f"{self.base_url}?$select=id&$filter={encoded_filter}"

            async with session.get(
                url, headers={"Authorization": f"Basic {self.auth_header}"}, timeout=10
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return len(data.get("value", []))
                _LOGGER.error(
                    "API responded with %s: %s", response.status, await response.text()
                )
                return None

        except Exception as err:
            _LOGGER.error("Error in _fetch_count: %s", err)
            raise

    async def _fetch_product_version(self, session) -> Optional[str]:
        """Fetch the product version from the API."""
        try:
            url = f"{self.host}/tas/api/productVersion"
            async with session.get(
                url, headers={"Authorization": f"Basic {self.auth_header}"}, timeout=10
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    major = data.get("major")
                    minor = data.get("minor")
                    patch = data.get("patch")
                    product_version = f"{major}.{minor}.{patch}"
                    _LOGGER.debug(
                        "API responded with product version: %s",
                        product_version,
                    )
                    if major is not None and minor is not None and patch is not None:
                        # Returns a string as "major.minor.patch"
                        return product_version
                    else:
                        _LOGGER.error("Incomplete version data: %s", data)
                        return None
                _LOGGER.error(
                    "API responded with %s: %s", response.status, await response.text()
                )
                return None
        except Exception as err:
            _LOGGER.error("Error in _fetch_product_version: %s", err)
            raise

    async def close(self) -> None:
        """Close the API session."""
        await self.session.close()
        _LOGGER.debug("API session closed for %s", self.host)
