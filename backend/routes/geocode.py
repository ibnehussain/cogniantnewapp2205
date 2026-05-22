"""
routes/geocode.py
GET /api/geocode?lat=<float>&lon=<float>
Reverse-geocodes browser coordinates to a city name.
"""

from flask import Blueprint, request, jsonify
from services.owm_client import reverse_geocode

geocode_bp = Blueprint("geocode", __name__)



@geocode_bp.route("/geocode")
def geocode():
    lat_str = request.args.get("lat", "").strip()
    lon_str = request.args.get("lon", "").strip()

    if not lat_str or not lon_str:
        return jsonify({"error": "Query parameters 'lat' and 'lon' are required."}), 400

    try:
        lat = float(lat_str)
        lon = float(lon_str)
    except ValueError:
        return jsonify({"error": "'lat' and 'lon' must be valid numbers."}), 400

    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        return jsonify({"error": "Coordinates are out of valid range."}), 400

    try:
        city = reverse_geocode(lat, lon)
        return jsonify({"city": city}), 200
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 404
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 502
