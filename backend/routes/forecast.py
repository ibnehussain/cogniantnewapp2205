"""
routes/forecast.py
GET /api/forecast?city=<name>
Returns 5-day forecast JSON shaped for the frontend.
"""

from flask import Blueprint, request, jsonify
from services.owm_client import get_forecast

forecast_bp = Blueprint("forecast", __name__)


@forecast_bp.route("/forecast")
def forecast():
    city = request.args.get("city", "").strip()

    if not city:
        return jsonify({"error": "Query parameter 'city' is required."}), 400

    if len(city) > 100:
        return jsonify({"error": "City name is too long."}), 400

    try:
        data = get_forecast(city)
        return jsonify(data), 200
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 404
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 502
