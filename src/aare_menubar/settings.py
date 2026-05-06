"""Settings persistence with JSON."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class SettingsManager:
    """Encapsulated user preferences backed by a JSON file."""

    _DEFAULT_REFRESH_MINUTES: int = 5
    _DEFAULT_UNIT: str = "C"          # "C" or "F"
    _DEFAULT_CITY: str = "bern"

    def __init__(self, filepath: str | Path | None = None) -> None:
        if filepath is None:
            filepath = Path.home() / ".aare_menubar_settings.json"
        self._filepath = Path(filepath)
        self._data: dict[str, Any] = {}
        self._load()

    # ---- public API --------------------------------------------------------

    def get_refresh_minutes(self) -> int:
        return self._data.get("refresh_minutes", self._DEFAULT_REFRESH_MINUTES)

    def set_refresh_minutes(self, value: int) -> None:
        self._data["refresh_minutes"] = max(1, int(value))
        self._save()

    def get_unit(self) -> str:
        unit = self._data.get("unit", self._DEFAULT_UNIT)
        return unit if unit in ("C", "F") else self._DEFAULT_UNIT

    def set_unit(self, value: str) -> None:
        if value in ("C", "F"):
            self._data["unit"] = value
            self._save()

    def get_city(self) -> str:
        return self._data.get("city", self._DEFAULT_CITY)

    def set_city(self, value: str) -> None:
        self._data["city"] = str(value).strip().lower()
        self._save()

    # ---- internals ---------------------------------------------------------

    def _load(self) -> None:
        if self._filepath.exists():
            try:
                raw = self._filepath.read_text(encoding="utf-8")
                self._data = json.loads(raw)
            except (json.JSONDecodeError, OSError):
                self._data = {}
        else:
            self._data = {}

    def _save(self) -> None:
        self._filepath.write_text(json.dumps(self._data, indent=2), encoding="utf-8")
