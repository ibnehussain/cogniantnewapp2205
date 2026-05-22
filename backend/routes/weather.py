"""
routes/weather.py
GET /api/weather?city=<name>
Returns current weather JSON shaped for the frontend.
"""

from flask import Blueprint, request, jsonify
from services.owm_client import get_current_weather

weather_bp = Blueprint("weather", __name__)


@weather_bp.route("/weather")
def weather():
    city = request.args.get("city", "").strip()

    if not city:
        return jsonify({"error": "Query parameter 'city' is required."}), 400

    # Basic length guard — OWM rejects absurdly long strings anyway
    if len(city) > 100:
        return jsonify({"error": "City name is too long."}), 400

    try:
        data = get_current_weather(city)
        return jsonify(data), 200
    except ValueError as exc:
        # City not found
        return jsonify({"error": str(exc)}), 404
    except RuntimeError as exc:
        # API key / network / upstream error
        return jsonify({"error": str(exc)}), 502
