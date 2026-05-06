"""Main rumps application — Aare temperature menubar."""
from __future__ import annotations

import threading
from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING

import rumps

from .service import AareService, DisplayData
from .settings import SettingsManager

if TYPE_CHECKING:
    from concurrent.futures import Future

_REFRESH_OPTIONS: list[int] = [1, 5, 10, 15, 30]


class AareMenubarApp(rumps.App):
    """Encapsulated rumps app. Owns service, settings, timer, and UI state."""

    def __init__(self) -> None:
        super().__init__(
            name="Aare",
            title="Aare …",
            icon=None,
            quit_button="Quit",
        )
        self._service = AareService()
        self._settings = SettingsManager()
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="aare_bg")

        # Menu items
        self._location_item = rumps.MenuItem("Location: …")
        self._flow_item = rumps.MenuItem("Flow: --")
        self._text_item = rumps.MenuItem("")
        self._error_item = rumps.MenuItem("")
        self._error_item.hidden = True

        self._city_menu = rumps.MenuItem("Cities")
        self._settings_menu = rumps.MenuItem("Settings")
        self._build_settings_submenu()

        self.menu = [
            self._location_item,
            self._flow_item,
            self._text_item,
            self._error_item,
            None,
            self._city_menu,
            self._settings_menu,
            None,
            rumps.MenuItem("Refresh Now", callback=self._on_manual_refresh),
        ]

        # Timers
        self._poll_timer = rumps.Timer(self._poll_result, 1)
        self._poll_timer.start()

        self._refresh_timer = rumps.Timer(
            self._on_refresh_timer,
            self._settings.get_refresh_minutes() * 60,
        )
        self._refresh_timer.start()

        # Mutable state for cross-thread communication
        self._pending_data: DisplayData | None = None
        self._lock = threading.Lock()

        # Bootstrap background tasks
        self._has_cities = False
        threading.Thread(target=self._load_cities_bg, daemon=True).start()
        self._trigger_refresh()

    # ---- public lifecycle ---------------------------------------------------

    def run(self) -> None:
        try:
            super().run()
        finally:
            self._executor.shutdown(wait=False)
            self._service.close()

    # ---- timer callbacks ----------------------------------------------------

    def _poll_result(self, _: rumps.Timer) -> None:
        """Polls pending data from background threads every second."""
        with self._lock:
            data = self._pending_data
            self._pending_data = None
        if data is not None:
            self._apply_display_data(data)

    def _on_refresh_timer(self, _: rumps.Timer) -> None:
        self._trigger_refresh()

    def _on_manual_refresh(self, _: rumps.MenuItem) -> None:
        self._trigger_refresh()

    # ---- settings callbacks -------------------------------------------------

    def _on_city_selected(self, sender: rumps.MenuItem) -> None:
        city = str(sender.title).lower().strip()
        self._settings.set_city(city)
        self._update_city_checkmarks()
        self._trigger_refresh()

    def _on_unit_selected(self, _: rumps.MenuItem, unit: str) -> None:
        self._settings.set_unit(unit)
        self._update_unit_checkmarks()
        self._trigger_refresh()

    def _on_refresh_selected(self, _: rumps.MenuItem, minutes: int) -> None:
        self._settings.set_refresh_minutes(minutes)
        self._update_refresh_checkmarks()
        self._refresh_timer.stop()
        self._refresh_timer = rumps.Timer(self._on_refresh_timer, minutes * 60)
        self._refresh_timer.start()

    # ---- display / UI ------------------------------------------------------

    def _apply_display_data(self, data: DisplayData) -> None:
        if data.error and data.temperature is None:
            self.title = "Aare: --"
            self._error_item.title = f"Error: {data.error[:80]}"
            self._error_item.hidden = False
        else:
            t = data.temperature
            u = data.unit
            self.title = f"{t}°{u} {data.icon}" if t is not None else f"Aare: -- {data.icon}"
            if data.error:
                self._error_item.title = f"Error: {data.error[:80]}"
                self._error_item.hidden = False
            else:
                self._error_item.hidden = True

        self._location_item.title = f"Location: {data.city_name}"
        self._flow_item.title = f"Flow: {data.flow if data.flow is not None else '--'} m³/s"
        self._text_item.title = data.text or ""

    # ---- refresh logic ------------------------------------------------------

    def _trigger_refresh(self) -> None:
        def _fetch() -> DisplayData:
            return self._service.fetch_current(
                self._settings.get_city(),
                self._settings.get_unit(),
            )

        def _done(future: Future[DisplayData]) -> None:
            try:
                result = future.result()
            except Exception as exc:
                city = self._settings.get_city()
                unit = self._settings.get_unit()
                result = DisplayData(
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
            with self._lock:
                self._pending_data = result

        future = self._executor.submit(_fetch)
        future.add_done_callback(_done)

    # ---- city submenu -------------------------------------------------------

    def _load_cities_bg(self) -> None:
        try:
            cities = self._service.fetch_cities()
        except Exception:
            return
        self._has_cities = True
        # Schedule UI update on main thread via a one-shot timer
        threading.Timer(0.2, self._populate_city_menu, args=(cities,)).start()

    def _populate_city_menu(self, cities: list) -> None:
        for city in cities:
            label = city.name or city.city
            item = rumps.MenuItem(label)
            item.set_callback(self._on_city_selected)
            self._city_menu.add(item)
        self._update_city_checkmarks()

    def _update_city_checkmarks(self) -> None:
        current = self._settings.get_city()
        for item in self._city_menu:
            if isinstance(item, rumps.MenuItem) and str(item.title).lower().strip() == current:
                item.state = 1
            elif isinstance(item, rumps.MenuItem):
                item.state = 0

    # ---- settings submenu ---------------------------------------------------

    def _build_settings_submenu(self) -> None:
        unit_menu = rumps.MenuItem("Unit")
        self._unit_c = rumps.MenuItem("°C")
        self._unit_c.set_callback(lambda s: self._on_unit_selected(s, "C"))
        self._unit_f = rumps.MenuItem("°F")
        self._unit_f.set_callback(lambda s: self._on_unit_selected(s, "F"))
        unit_menu.add(self._unit_c)
        unit_menu.add(self._unit_f)
        self._settings_menu.add(unit_menu)

        refresh_menu = rumps.MenuItem("Refresh Interval")
        self._refresh_items: dict[int, rumps.MenuItem] = {}
        for minutes in _REFRESH_OPTIONS:
            lbl = f"{minutes} min"
            item = rumps.MenuItem(lbl)
            item.set_callback(lambda s, m=minutes: self._on_refresh_selected(s, m))
            self._refresh_items[minutes] = item
            refresh_menu.add(item)
        self._settings_menu.add(refresh_menu)

        self._update_unit_checkmarks()
        self._update_refresh_checkmarks()

    def _update_unit_checkmarks(self) -> None:
        unit = self._settings.get_unit()
        self._unit_c.state = 1 if unit == "C" else 0
        self._unit_f.state = 1 if unit == "F" else 0

    def _update_refresh_checkmarks(self) -> None:
        current = self._settings.get_refresh_minutes()
        for minutes, item in self._refresh_items.items():
            item.state = 1 if minutes == current else 0
