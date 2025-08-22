import asyncio
import base64
from typing import Optional

import aiohttp

from .constants import (
    API_URL,
    LOCK_ID_URL,
    LOCKS_ID_URL,
    SUPPORTED_LOCK_TYPES,
    TOGGLE_LOCK_URL,
)
from .exceptions import AuthorizationFailedExcepion, BadRequestException, UpdateFailed


class GlueLock:
    def __init__(
        self,
        username: str,
        password: str,
        api_key: Optional[str] = None,
        lock_id: Optional[str] = None,
        session: aiohttp.ClientSession | None = None,
    ):
        self.username = username
        self.password = password
        self.api_key = api_key
        self.lock_id = lock_id
        self.headers = None
        self._battery = None
        self._last_event = None
        self._serial_number = None
        self._description = None
        if not session:
            self.session = aiohttp.ClientSession()
        else:
            self.session = session

    @property
    def is_connected(self):
        if self.api_key and self.lock_id and self.headers:
            return True
        return False

    async def update(self):
        """Update the lock information."""
        if not self.is_connected:
            await self.connect()
        try:
            await self.get_battery_status()
            await self.get_last_event()
            await self.get_serial_number()
            await self.get_description()
        except Exception as e:
            raise UpdateFailed(f"Failed to update lock data: {e}") from e

    async def connect(self):
        """Establish a connection to the Glue API."""
        if not self.api_key:
            self.api_key = await self.create_glue_api_key()
            self.headers = {
                "Content-Type": "application/json",
                "Authorization": f"Api-Key {self.api_key}",
            }
        else:
            self.headers = {
                "Content-Type": "application/json",
                "Authorization": f"Api-Key {self.api_key}",
            }

    async def get_lock_id_from_name(self, name: str) -> str:
        """Retrieve the lock ID associated with the given name."""
        all_locks = await self.get_all_locks()
        return [lock for lock in all_locks if name == lock["name"]][0]["id"]

    async def get_all_locks(self):
        """Retrieve all locks associated with the API key."""
        async with self.session.get(LOCKS_ID_URL, headers=self.headers) as response:
            if response.status == 200:
                response_data = await response.json()
                return [
                    {
                        "id": lock_info.get("id"),
                        "name": lock_info.get("description"),
                    }
                    for lock_info in response_data
                ]
            text = await response.text()
            raise BadRequestException(
                f"Failed to retrieve lock ID: {response.status} - {text}"
            )

    async def get_serial_number(self):
        """Retrieve the serial number of the lock."""
        response = await self.get_lock_info_request()
        self._serial_number = response.get("serialNumber")
        return self._serial_number

    async def get_description(self):
        """Retrieve the description of the lock."""
        response = await self.get_lock_info_request()
        self._description = response.get("description")
        return self._description

    async def get_last_event(self):
        """Retrieve the last event of the lock."""
        response = await self.get_lock_info_request()
        last_event = {
            "event_type": response.get("eventType"),
            "timestamp": response.get("eventTime"),
        }
        self._last_event = last_event
        return last_event

    async def get_battery_status(self):
        """Retrieve the battery status of the lock."""
        response = await self.get_lock_info_request()
        self._battery = response.get("batteryStatus")
        return self._battery

    async def get_firmware_version(self):
        """Retrieve the firmware version of the lock."""
        response = await self.get_lock_info_request()
        self._firmware_version = response.get("firmwareVersion")
        return self._firmware_version

    async def get_lock_info_request(self):
        """Retrieve information about the specific lock."""
        url = LOCK_ID_URL.format(lock_id=self.lock_id)

        async with self.session.get(url, headers=self.headers) as response:
            if response.status == 200:
                return await response.json()
            text = await response.text()
            raise BadRequestException(
                f"Failed to retrieve lock info: {response.status} - {text}"
            )

    async def control_lock(self, type: str):
        """Control the lock (lock or unlock)."""
        if type not in SUPPORTED_LOCK_TYPES:
            raise ValueError(
                f"Invalid lock type: {type}. Accepted types are: {SUPPORTED_LOCK_TYPES}"
            )

        url = TOGGLE_LOCK_URL.format(lock_id=self.lock_id)
        payload = {
            "type": type  # e.g., "unlock" or "lock"
        }

        async with self.session.post(
            url, headers=self.headers, json=payload
        ) as response:
            if response.status in (
                200,
                201,
                202,
            ):  # 202 may mean async operation started
                return await response.json()
            text = await response.text()
            raise BadRequestException(
                f"Lock operation failed: {response.status} - {text}"
            )

    async def create_glue_api_key(self):
        """Create the Basic Auth header."""
        credentials = f"{self.username}:{self.password}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {encoded_credentials}",
        }
        payload = {
            "name": "GlueLock API Key",
            "scopes": ["events.read", "locks.read", "locks.write"],
        }

        async with self.session.post(
            API_URL, json=payload, headers=headers
        ) as response:
            if response.status in [200, 201]:
                response_data = await response.json()
                return response_data.get("apiKey")
            text = await response.text()
            raise AuthorizationFailedExcepion(
                f"API key creation failed: {response.status} - {text}"
            )
