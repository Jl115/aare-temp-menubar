"""Map Aare temperature (°C) to display emoji."""
from __future__ import annotations


class IconMapper:
    """Pure utility: temperature → emoji. No state."""

    # None in low means open-ended below; None in high means open-ended above.
    _BANDS: list[tuple[float | None, float | None, str]] = [
        (None, 10.0, "🥶"),
        (10.0, 15.0, "❄️"),
        (15.0, 20.0, "🌊"),
        (20.0, 25.0, "🏊"),
        (25.0, None, "🔥"),
    ]

    @classmethod
    def for_celsius(cls, temp: float | None) -> str:
        """Return emoji for a given Celsius value."""
        if temp is None:
            return "❓"
        for low, high, emoji in cls._BANDS:
            if low is None and (high is None or temp < high):
                return emoji
            if high is None and (low is not None and temp >= low):
                return emoji
            if low is not None and high is not None and low <= temp < high:
                return emoji
        return "❓"
