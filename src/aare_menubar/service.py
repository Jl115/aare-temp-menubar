"""Business-logic service: fetch, cache, convert."""
from __future__ import annotations

from dataclasses import dataclass

from .client import AareAPIClient
from .icons import IconMapper
from .models import AareCurrentData, CitySummary


@dataclass(frozen=True, slots=True)
class DisplayData:
    """Clean DTO for UI consumption."""
    temperature: float | None
    unit: str               # "C" or "F"
    icon: str
    city_name: str
    flow: float | None
    flow_text: str | None
    text: str | None
    timestamp: int | None
    error: str | None = None


class AareService:
    """Encapsulated service layer. Owns the API client and last-known cache."""

    def __init__(self) -> None:
        self._client = AareAPIClient()
        self._cities: list[CitySummary] | None = None
        self._last_data: AareCurrentData | None = None

    # ---- public API --------------------------------------------------------

    def fetch_current(self, city: str, unit: str) -> DisplayData:
        """Fetch fresh data and return a DisplayData DTO."""
        try:
            data = self._client.fetch_current(city)
        except Exception as exc:
            data = self._last_data
            if data is None:
                return DisplayData(
                    temperature=None,
                    unit=unit,
                    icon="❓",
                    city_name=city.capitalize(),
                    flow=None,
                    flow_text=None,
                    text=None,
                    timestamp=None,
                    error=str(exc),
                )
            error_msg = str(exc)
        else:
            self._last_data = data
            error_msg = None

        aare = data.aare
        temp = aare.temperature_prec if aare is not None else None
        if temp is None and aare is not None:
            temp = aare.temperature

        display_temp = self._convert(temp, unit)
        icon = IconMapper.for_celsius(temp)

        return DisplayData(
            temperature=display_temp,
            unit=unit,
            icon=icon,
            city_name=(aare.location if aare is not None else None) or city.capitalize(),
            flow=aare.flow if aare is not None else None,
            flow_text=aare.flow_text if aare is not None else None,
            text=aare.temperature_text if aare is not None else None,
            timestamp=aare.timestamp if aare is not None else None,
            error=error_msg,
        )

    def fetch_cities(self) -> list[CitySummary]:
        """Return cached city list or fetch from API."""
        if self._cities is not None:
            return self._cities
        cities = self._client.fetch_cities()
        self._cities = cities
        return cities

    def close(self) -> None:
        self._client.close()

    # ---- internals ---------------------------------------------------------

    @staticmethod
    def _convert(celsius: float | None, unit: str) -> float | None:
        if celsius is None:
            return None
        if unit == "F":
            return round(celsius * 9 / 5 + 32, 1)
        return round(celsius, 1)
