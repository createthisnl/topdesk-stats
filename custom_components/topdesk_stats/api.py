"""
Coordinator for TOPdesk Statistics integration.

topdesk_stats/coordinator.py
"""

from __future__ import annotations

import base64
import hashlib
import logging
import urllib.parse
from datetime import UTC, datetime
from typing import Self

import aiohttp
from aiohttp import ClientError, ClientSession, ClientTimeout, InvalidURL

from .const import (
    API_CHANGE_BASE_PATH,
    API_INCIDENT_BASE_PATH,
    STATUS_200,
)

_LOGGER = logging.getLogger(__name__)


class TOPdeskAPI:
    """Handles communication with the TOPdesk API."""

    def __init__(
        self,
        instance_host: str,
        instance_username: str,
        instance_password: str,
        instance_name: str,
        api_type: str = "incident",  # Defaults to incidents
    ) -> None:
        """Initialize for communication."""
        self.instance_name = instance_name
        self.instance_version = ""
        self.host = instance_host.rstrip("/")
        self.api_type = api_type.lower()  # Make it case insensitive

        # Dynamically set the base_url based on api_type
        if self.api_type == "change":
            self.base_url = f"{self.host}{API_CHANGE_BASE_PATH}"
        else:  # Defaults to incident
            self.base_url = f"{self.host}{API_INCIDENT_BASE_PATH}"

        self.base_url = f"{self.host}" + API_INCIDENT_BASE_PATH
        self.device_id = hashlib.sha256(
            f"{self.host}_{instance_name}".encode()
        ).hexdigest()[:10]
        self.auth_header = base64.b64encode(
            f"{instance_username}:{instance_password}".encode()
        ).decode()
        self.timeout = ClientTimeout(total=15)
        self.session = None  # The session will be initialized later
        _LOGGER.debug(
            "Initialized TOPdeskAPI for %s: %s", self.instance_name, self.host
        )

    async def __aenter__(self) -> Self:
        """Start the client session."""
        self.session = aiohttp.ClientSession()
        if self.session:
            _LOGGER.debug("API session started for %s", self.host)
        return self

    async def __aexit__(
        self,
        *excinfo: object,
    ) -> bool | None:
        """Make sure the session is closed."""
        if self.session:
            await self.session.close()
            _LOGGER.debug("API session closed for %s", self.host)
        return

    def _generate_device_id(self) -> str:
        """Generate a unique device ID based on the host name."""
        return hashlib.sha256(self.host.encode()).hexdigest()[:10]

    async def fetch_version(self) -> str | None:
        """Fetch the product version."""
        try:
            if self.session is None:
                msg = "Session is not initialized"
                raise ValueError(msg)  # noqa: TRY301
            return await self._fetch_product_version(self.session)
        except Exception:
            _LOGGER.exception("Error fetching version:")
            return None

    async def test_connection(self) -> bool:
        """Test API connectivity."""
        try:
            if not self.host.startswith(("http://", "https://")):
                msg = "Invalid URL protocol"
                raise InvalidURL(msg)  # noqa: TRY301

            version = await self.fetch_version()
            if version is None:
                msg = "Unable to get product version"
                raise ValueError(msg)  # noqa: TRY301

        except InvalidURL:
            _LOGGER.exception("Error in URL:")
            return False
        except ClientError:
            _LOGGER.exception("API connection error:")
            return False
        except Exception:
            _LOGGER.exception("Connection test failed:")
            return False

        else:
            return True

        finally:
            if self.session:
                await self.close()

    async def fetch_tickets(
        self,
    ) -> tuple[int | None, int | None, int | None, int | None]:
        """Fetch ticket counts using OData queries."""
        try:
            if self.session is None:
                msg = "Session is not initialized"
                raise ValueError(msg)  # noqa: TRY301
            completed_count = await self._fetch_count(
                self.session, "(completed eq true)"
            )
            closed_completed_count = await self._fetch_count(
                self.session, "(completed eq true) and (closed eq true)"
            )
            new_today_count = await self._fetch_new_today_count(self.session)
            completed_today_count = await self._fetch_completed_today_count(
                self.session
            )
            return (  # noqa: TRY300
                completed_count,
                closed_completed_count,
                new_today_count,
                completed_today_count,
            )
        except Exception:
            _LOGGER.exception("API error:")
            return None, None, None, None

    async def _fetch_new_today_count(self, session: ClientSession) -> int | None:
        """Fetch new tickets created today."""
        today = datetime.now(UTC).strftime("%Y-%m-%dT00:00:00Z")
        filter_query = f"(creationDate ge {today})"
        return await self._fetch_count(session, filter_query)

    async def _fetch_completed_today_count(self, session: ClientSession) -> int | None:
        """Fetch completed tickets created today."""
        today = datetime.now(UTC).strftime("%Y-%m-%dT00:00:00Z")
        filter_query = (
            f"(creationDate ge {today}) and (completed eq true) and (closed eq false)"
        )
        return await self._fetch_count(session, filter_query)

    async def _fetch_count(
        self, session: ClientSession, filter_query: str
    ) -> int | None:
        """Fetch count using original working method."""
        try:
            encoded_filter = urllib.parse.quote(filter_query)
            url = f"{self.base_url}?$select=id&$filter={encoded_filter}"
            timeout = ClientTimeout(total=10)
            async with session.get(
                url,
                headers={"Authorization": f"Basic {self.auth_header}"},
                timeout=timeout,
            ) as response:
                if response.status == STATUS_200:
                    data = await response.json()
                    return len(data.get("value", []))
                _LOGGER.error(
                    "API responded with %s: %s", response.status, await response.text()
                )
                return None

        except Exception:
            _LOGGER.exception("Error in _fetch_count")
            raise

    async def _fetch_product_version(self, session: ClientSession) -> str | None:
        """Fetch the product version from the API."""
        try:
            url = f"{self.host}/tas/api/productVersion"
            timeout = ClientTimeout(total=10)
            async with session.get(
                url,
                headers={"Authorization": f"Basic {self.auth_header}"},
                timeout=timeout,
            ) as response:
                if response.status == STATUS_200:
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
                        return product_version

                    _LOGGER.error("Incomplete version data: %s", data)
                    return None
                _LOGGER.error(
                    "API responded with %s: %s", response.status, await response.text()
                )
                return None
        except Exception:
            _LOGGER.exception("Error in _fetch_product_version:")
            raise

    async def close(self) -> None:
        """Close the API session."""
        if self.session:
            await self.session.close()
            _LOGGER.debug("API session closed for %s", self.host)
