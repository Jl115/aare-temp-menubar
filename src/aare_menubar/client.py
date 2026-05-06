"""HTTP client for Aare.guru API — synchronous version for rumps compatibility."""
from __future__ import annotations

import httpx

from .models import AareCurrentData, CitySummary


BASE_URL = "https://aareguru.existenz.ch"
APP_ID = "aare.temp.menubar"
APP_VERSION = "1.0.0"


class AareAPIClient:
    """Encapsulated sync client for Aare.guru v2018 endpoints."""

    def __init__(self, base_url: str = BASE_URL, timeout: float = 10.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._client = httpx.Client(timeout=timeout)

    def fetch_cities(self) -> list[CitySummary]:
        """Return all available measurement cities."""
        url = f"{self._base_url}/v2018/cities"
        params = {"app": APP_ID, "version": APP_VERSION}
        response = self._client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return [CitySummary.model_validate(item) for item in data]

    def fetch_current(self, city: str) -> AareCurrentData:
        """Return full current data for a given city."""
        url = f"{self._base_url}/v2018/current"
        params = {"city": city, "app": APP_ID, "version": APP_VERSION}
        response = self._client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return AareCurrentData.model_validate(data)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> AareAPIClient:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
