"""Pydantic models for Aare.guru API responses."""
from __future__ import annotations

from pydantic import BaseModel, Field


class Coordinates(BaseModel):
    lat: float | None = None
    lon: float | None = None


class CitySummary(BaseModel):
    city: str
    name: str
    longname: str | None = None
    coordinates: Coordinates | None = None
    aare: float | None = None
    aare_prec: float | None = None
    sy: int | None = None
    tn: float | None = None
    tx: float | None = None
    forecast: bool | None = None
    time: int | None = None
    url: str | None = None
    today: str | None = None
    widget: str | None = None
    history: str | None = None


class AareDetail(BaseModel):
    location: str | None = None
    location_long: str | None = None
    coordinates: Coordinates | None = None
    forecast: bool | None = None
    timestamp: int | None = None
    timestring: str | None = None
    temperature: float | None = None
    temperature_prec: float | None = None
    temperature_text: str | None = None
    temperature_text_short: str | None = None
    flow: float | None = None
    flow_text: str | None = None
    flow_scale_threshold: float | None = None
    forecast2h: float | None = None


class AareCurrentData(BaseModel):
    aare: AareDetail | None = Field(default=None, alias="aare")
    # Other top-level keys (weather, aarepast, sun) are ignored for the menubar use case.
