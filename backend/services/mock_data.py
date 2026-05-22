"""
services/mock_data.py
Realistic static weather data for local development and testing.
Activated when USE_MOCK_DATA=true is set in .env.

Cities with full data: London, New York, Tokyo, Sydney, Dubai, Paris.
Any other city name falls back to the "London" dataset.
"""

import time
from datetime import datetime, timezone, timedelta

# ── Helpers ────────────────────────────────────────────────────

def _unix(dt: datetime) -> int:
    return int(dt.timestamp())


_NOW = _unix(datetime.now(tz=timezone.utc))

# Pre-baked sunrise/sunset for each city (local clock times stored as UTC unix)
_CITIES = {
    "london": {
        "city": "London", "country": "GB",
        "temp": 14.3, "feels_like": 12.8, "humidity": 72,
        "pressure": 1012, "wind_speed": 5.1, "visibility": 9000,
        "description": "overcast clouds", "icon": "04d",
        "sunrise": _unix(datetime(2026, 5, 21, 4, 57, tzinfo=timezone.utc)),
        "sunset":  _unix(datetime(2026, 5, 21, 20, 8, tzinfo=timezone.utc)),
        "timezone": 3600,
    },
    "new york": {
        "city": "New York", "country": "US",
        "temp": 22.6, "feels_like": 21.9, "humidity": 55,
        "pressure": 1018, "wind_speed": 3.7, "visibility": 10000,
        "description": "few clouds", "icon": "02d",
        "sunrise": _unix(datetime(2026, 5, 21, 9, 26, tzinfo=timezone.utc)),
        "sunset":  _unix(datetime(2026, 5, 21, 23, 59, tzinfo=timezone.utc)),
        "timezone": -14400,
    },
    "tokyo": {
        "city": "Tokyo", "country": "JP",
        "temp": 27.1, "feels_like": 29.4, "humidity": 80,
        "pressure": 1008, "wind_speed": 2.3, "visibility": 7000,
        "description": "light rain", "icon": "10d",
        "sunrise": _unix(datetime(2026, 5, 20, 19, 58, tzinfo=timezone.utc)),
        "sunset":  _unix(datetime(2026, 5, 21, 9, 51, tzinfo=timezone.utc)),
        "timezone": 32400,
    },
    "sydney": {
        "city": "Sydney", "country": "AU",
        "temp": 17.0, "feels_like": 16.2, "humidity": 63,
        "pressure": 1021, "wind_speed": 4.5, "visibility": 10000,
        "description": "clear sky", "icon": "01d",
        "sunrise": _unix(datetime(2026, 5, 20, 21, 26, tzinfo=timezone.utc)),
        "sunset":  _unix(datetime(2026, 5, 21, 7, 3, tzinfo=timezone.utc)),
        "timezone": 36000,
    },
    "dubai": {
        "city": "Dubai", "country": "AE",
        "temp": 38.5, "feels_like": 41.2, "humidity": 42,
        "pressure": 1002, "wind_speed": 6.2, "visibility": 8000,
        "description": "sunny", "icon": "01d",
        "sunrise": _unix(datetime(2026, 5, 21, 2, 16, tzinfo=timezone.utc)),
        "sunset":  _unix(datetime(2026, 5, 21, 15, 5, tzinfo=timezone.utc)),
        "timezone": 14400,
    },
    "paris": {
        "city": "Paris", "country": "FR",
        "temp": 18.7, "feels_like": 17.5, "humidity": 65,
        "pressure": 1015, "wind_speed": 4.0, "visibility": 10000,
        "description": "partly cloudy", "icon": "03d",
        "sunrise": _unix(datetime(2026, 5, 21, 4, 3, tzinfo=timezone.utc)),
        "sunset":  _unix(datetime(2026, 5, 21, 20, 10, tzinfo=timezone.utc)),
        "timezone": 7200,
    },
}

_FORECAST_TEMPLATES = {
    "london":   [("light rain",      "10d", 15, 9),  ("overcast clouds", "04d", 13, 8),  ("moderate rain",  "09d", 12, 7),  ("few clouds",     "02d", 16, 10), ("clear sky",      "01d", 18, 11)],
    "new york": [("clear sky",       "01d", 24, 16), ("few clouds",      "02d", 26, 17), ("scattered clouds","03d",22, 14), ("thunderstorm",   "11d", 19, 13), ("clear sky",      "01d", 25, 15)],
    "tokyo":    [("heavy rain",      "09d", 25, 20), ("light rain",      "10d", 26, 21), ("overcast clouds", "04d", 27, 22), ("few clouds",     "02d", 29, 22), ("clear sky",      "01d", 30, 23)],
    "sydney":   [("clear sky",       "01d", 18, 12), ("few clouds",      "02d", 19, 13), ("clear sky",       "01d", 17, 11), ("partly cloudy",  "03d", 16, 10), ("light rain",     "10d", 15, 9)],
    "dubai":    [("sunny",           "01d", 39, 30), ("sunny",           "01d", 40, 31), ("haze",            "50d", 38, 29), ("sunny",          "01d", 41, 31), ("few clouds",     "02d", 37, 28)],
    "paris":    [("partly cloudy",   "03d", 20, 13), ("light rain",      "10d", 17, 11), ("overcast clouds", "04d", 16, 10), ("clear sky",      "01d", 22, 14), ("few clouds",     "02d", 23, 15)],
}


def _lookup(city: str) -> str:
    """Return the normalised key; fall back to 'london' for unknown cities."""
    return city.lower() if city.lower() in _CITIES else "london"


# ── Public interface (mirrors owm_client.py) ───────────────────

def mock_get_current_weather(city: str) -> dict:
    key = _lookup(city)
    d = _CITIES[key]
    return {
        "city":        d["city"],
        "country":     d["country"],
        "dt":          _NOW,
        "timezone":    d["timezone"],
        "temp":        d["temp"],
        "feels_like":  d["feels_like"],
        "humidity":    d["humidity"],
        "pressure":    d["pressure"],
        "wind_speed":  d["wind_speed"],
        "visibility":  d["visibility"],
        "uv_index":    5,
        "description": d["description"],
        "icon":        d["icon"],
        "sunrise":     d["sunrise"],
        "sunset":      d["sunset"],
    }


def mock_get_forecast(city: str) -> dict:
    key = _lookup(city)
    templates = _FORECAST_TEMPLATES.get(key, _FORECAST_TEMPLATES["london"])
    forecast = []
    for i, (desc, icon, t_max, t_min) in enumerate(templates):
        day_dt = _unix(datetime.now(tz=timezone.utc) + timedelta(days=i + 1))
        forecast.append({
            "dt":          day_dt,
            "temp_max":    t_max,
            "temp_min":    t_min,
            "description": desc,
            "icon":        icon,
        })
    return {"forecast": forecast}


def mock_reverse_geocode(lat: float, lon: float) -> str:
    """Return a city name based on rough lat/lon bounding boxes."""
    if 49 <= lat <= 52 and -1 <= lon <= 1:
        return "London"
    if 35 <= lat <= 41 and -75 <= lon <= -72:
        return "New York"
    if 35 <= lat <= 36 and 139 <= lon <= 140:
        return "Tokyo"
    if -34 <= lat <= -33 and 150 <= lon <= 152:
        return "Sydney"
    if 24 <= lat <= 26 and 54 <= lon <= 56:
        return "Dubai"
    if 48 <= lat <= 49 and 2 <= lon <= 3:
        return "Paris"
    return "London"
