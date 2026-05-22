"""
app.py — Flask application factory and entry point.
Run locally:  python app.py
Production:   gunicorn -w 4 "app:create_app()"
"""

import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv

# Load .env before anything else reads os.environ
load_dotenv()

# ── Shared extensions (initialised in create_app) ──────────────
cache = Cache()
limiter = Limiter(key_func=get_remote_address, default_limits=["60 per minute"])


def create_app() -> Flask:
    app = Flask(__name__)

    # ── Config ─────────────────────────────────────────────────
    app.config["CACHE_TYPE"] = "SimpleCache"        # swap for RedisCache in prod
    app.config["CACHE_DEFAULT_TIMEOUT"] = 600       # 10 minutes

    # ── Extensions ─────────────────────────────────────────────
    # In development, allow all origins (covers file:// → null origin).
    # In production, restrict to the explicit FRONTEND_ORIGIN env var.
    is_dev = os.environ.get("FLASK_ENV", "production") == "development"
    cors_origins = "*" if is_dev else os.environ.get("FRONTEND_ORIGIN", "")
    CORS(app, origins=cors_origins)

    cache.init_app(app)
    limiter.init_app(app)

    # ── Blueprints ──────────────────────────────────────────────
    from routes.weather  import weather_bp
    from routes.forecast import forecast_bp
    from routes.geocode  import geocode_bp

    app.register_blueprint(weather_bp,  url_prefix="/api")
    app.register_blueprint(forecast_bp, url_prefix="/api")
    app.register_blueprint(geocode_bp,  url_prefix="/api")

    # ── Global error handlers ───────────────────────────────────
    @app.errorhandler(404)
    def not_found(exc):
        return jsonify({"error": "Endpoint not found."}), 404

    @app.errorhandler(405)
    def method_not_allowed(exc):
        return jsonify({"error": "Method not allowed."}), 405

    @app.errorhandler(429)
    def rate_limit_exceeded(exc):
        return jsonify({"error": "Too many requests. Please slow down."}), 429

    @app.errorhandler(500)
    def internal_error(exc):
        return jsonify({"error": "Internal server error."}), 500

    return app


if __name__ == "__main__":
    flask_app = create_app()
    debug_mode = os.environ.get("FLASK_ENV", "production") == "development"
    flask_app.run(host="127.0.0.1", port=5000, debug=debug_mode)
