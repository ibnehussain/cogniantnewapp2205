"""
services/owm_client.py
Low-level wrapper around the OpenWeatherMap API.
All direct HTTP calls to OWM live here; routes never call OWM directly.

Set USE_MOCK_DATA=true in .env to return realistic static data without
needing a real OWM API key (useful for local development and testing).
"""

import os
import requests


def _use_mock() -> bool:
    return os.environ.get("USE_MOCK_DATA", "false").lower() == "true"

OWM_BASE = "https://api.openweathermap.org"


def _api_key() -> str:
    key = os.environ.get("OWM_API_KEY", "")
    if not key:
        raise RuntimeError("OWM_API_KEY is not set in environment variables.")
    return key


def _get(path: str, params: dict) -> dict:
    """Shared GET helper; raises ValueError on 404, RuntimeError on other errors."""
    params["appid"] = _api_key()
    params.setdefault("units", "metric")

    try:
        resp = requests.get(f"{OWM_BASE}{path}", params=params, timeout=8)
    except requests.exceptions.Timeout:
        raise RuntimeError("OpenWeatherMap request timed out.")
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"Network error: {exc}") from exc

    if resp.status_code == 404:
        raise ValueError("City not found.")
    if resp.status_code == 401:
        raise RuntimeError("Invalid OWM API key.")
    if not resp.ok:
        raise RuntimeError(f"OWM error {resp.status_code}: {resp.text[:120]}")

    return resp.json()


# ── Current Weather ────────────────────────────────────────────

def get_current_weather(city: str) -> dict:
    """
    Fetch current weather and shape it for the frontend.
    Returns a flat dict with the fields the UI expects.
    """
    if _use_mock():
        from services.mock_data import mock_get_current_weather
        return mock_get_current_weather(city)

    raw = _get("/data/2.5/weather", {"q": city})

    return {
        "city":        raw["name"],
        "country":     raw["sys"]["country"],
        "dt":          raw["dt"],
        "timezone":    raw["timezone"],
        "temp":        raw["main"]["temp"],
        "feels_like":  raw["main"]["feels_like"],
        "humidity":    raw["main"]["humidity"],
        "pressure":    raw["main"]["pressure"],
        "wind_speed":  raw["wind"]["speed"],
        "visibility":  raw.get("visibility", 0),
        "uv_index":    None,          # requires a separate OWM call; placeholder
        "description": raw["weather"][0]["description"],
        "icon":        raw["weather"][0]["icon"],
        "sunrise":     raw["sys"]["sunrise"],
        "sunset":      raw["sys"]["sunset"],
    }


# ── 5-Day Forecast ─────────────────────────────────────────────

def get_forecast(city: str) -> dict:
    """
    Fetch 5-day / 3-hour forecast and reduce to one entry per day (noon slot).
    Returns { forecast: [ { dt, temp_max, temp_min, description, icon }, ... ] }
    """
    if _use_mock():
        from services.mock_data import mock_get_forecast
        return mock_get_forecast(city)

    raw = _get("/data/2.5/forecast", {"q": city, "cnt": 40})

    # Group by calendar date, keep the slot closest to 12:00
    from collections import defaultdict
    from datetime import datetime, timezone

    days: dict[str, list] = defaultdict(list)
    for entry in raw["list"]:
        date_key = datetime.fromtimestamp(entry["dt"], tz=timezone.utc).strftime("%Y-%m-%d")
        days[date_key].append(entry)

    forecast = []
    for date_key in sorted(days.keys())[:5]:
        slots = days[date_key]
        # Pick slot closest to noon UTC
        noon_slot = min(
            slots,
            key=lambda e: abs(
                datetime.fromtimestamp(e["dt"], tz=timezone.utc).hour - 12
            ),
        )
        temps = [s["main"]["temp"] for s in slots]
        forecast.append({
            "dt":          noon_slot["dt"],
            "temp_max":    max(temps),
            "temp_min":    min(temps),
            "description": noon_slot["weather"][0]["description"],
            "icon":        noon_slot["weather"][0]["icon"],
        })

    return {"forecast": forecast}


# ── Reverse Geocode ────────────────────────────────────────────

def reverse_geocode(lat: float, lon: float) -> str:
    """Return a city name for the given coordinates."""
    if _use_mock():
        from services.mock_data import mock_reverse_geocode
        return mock_reverse_geocode(lat, lon)

    results = _get(
        "/geo/1.0/reverse",
        {"lat": lat, "lon": lon, "limit": 1},
    )
    if not results:
        raise ValueError("No location found for these coordinates.")
    entry = results[0]
    return entry.get("local_names", {}).get("en") or entry["name"]
