"""Tests for aare_menubar."""
from __future__ import annotations

import pytest

from aare_menubar.icons import IconMapper
from aare_menubar.service import AareService
from aare_menubar.settings import SettingsManager


class TestIconMapper:
    """Pure utility tests."""

    @pytest.mark.parametrize(
        ("temp", "expected"),
        [
            (5.0, "🥶"),
            (10.0, "❄️"),
            (12.5, "❄️"),
            (15.0, "🌊"),
            (18.0, "🌊"),
            (20.0, "🏊"),
            (23.0, "🏊"),
            (25.0, "🔥"),
            (30.0, "🔥"),
            (None, "❓"),
        ],
    )
    def test_for_celsius(self, temp: float | None, expected: str) -> None:
        assert IconMapper.for_celsius(temp) == expected


class TestSettingsManager:
    """Settings persistence tests against a temporary file."""

    def test_defaults(self, tmp_path) -> None:
        sm = SettingsManager(filepath=tmp_path / "settings.json")
        assert sm.get_city() == "bern"
        assert sm.get_unit() == "C"
        assert sm.get_refresh_minutes() == 5

    def test_round_trip(self, tmp_path) -> None:
        sm = SettingsManager(filepath=tmp_path / "settings.json")
        sm.set_city("thun")
        sm.set_unit("F")
        sm.set_refresh_minutes(10)

        sm2 = SettingsManager(filepath=tmp_path / "settings.json")
        assert sm2.get_city() == "thun"
        assert sm2.get_unit() == "F"
        assert sm2.get_refresh_minutes() == 10

    def test_unit_validation(self, tmp_path) -> None:
        sm = SettingsManager(filepath=tmp_path / "settings.json")
        sm.set_unit("X")
        assert sm.get_unit() == "C"  # falls back to default

    def test_refresh_clamping(self, tmp_path) -> None:
        sm = SettingsManager(filepath=tmp_path / "settings.json")
        sm.set_refresh_minutes(-3)
        assert sm.get_refresh_minutes() == 1


class TestAareService:
    """Integration-lite tests with real API calls (read-only)."""

    def test_fetch_current_bern(self) -> None:
        svc = AareService()
        data = svc.fetch_current("bern", "C")
        svc.close()

        assert data.temperature is not None
        assert data.unit == "C"
        assert data.city_name
        assert data.text
        assert data.error is None

    def test_fetch_current_fahrenheit(self) -> None:
        svc = AareService()
        celsius = svc.fetch_current("bern", "C")
        fahrenheit = svc.fetch_current("bern", "F")
        svc.close()

        assert celsius.temperature is not None
        assert fahrenheit.temperature is not None
        expected = round(celsius.temperature * 9 / 5 + 32, 1)
        assert fahrenheit.temperature == pytest.approx(expected, rel=1e-2)

    def test_fetch_cities(self) -> None:
        svc = AareService()
        cities = svc.fetch_cities()
        svc.close()

        assert cities
        names = [c.name for c in cities]
        assert "Bärn" in names or "Bern" in names
