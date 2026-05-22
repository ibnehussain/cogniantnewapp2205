# Weather Dashboard (Flask + Vanilla JS)

A full-stack weather dashboard with:
- **Flask backend API** that proxies OpenWeatherMap requests and protects the API key.
- **Vanilla JavaScript frontend** for city search, geolocation lookup, current weather, and 5-day forecast.
- **Mock data mode** for local development without a live OpenWeatherMap key.

---

## Project Structure

```text
cogniantnewapp2205/
├── backend/
│   ├── app.py                 # Flask app factory + entrypoint
│   ├── routes/                # /api/weather, /api/forecast, /api/geocode
│   ├── services/              # OWM integration + mock data
│   ├── tests/                 # Backend tests
│   ├── requirements.txt
│   ├── pytest.ini
│   └── .env.example
└── frontend/
    ├── index.html             # Main UI
    ├── css/styles.css         # Styling
    └── js/
        ├── api.js             # Calls backend endpoints
        ├── ui.js              # DOM rendering + unit toggle
        └── app.js             # Event wiring and app flow
```

---

## How It Works

1. User enters a city (or uses geolocation) in the frontend.
2. Frontend calls backend endpoints under `http://127.0.0.1:5000/api`.
3. Backend validates input, calls OpenWeatherMap (or mock provider), normalizes response shape, and returns JSON.
4. Frontend renders:
   - Current weather card
   - 5-day forecast strip
   - Error states and loading indicator

---

## Prerequisites

- Python **3.10+**
- `pip`
- A static file server for `frontend/` (for example VS Code Live Server, `python -m http.server`, etc.)
- (Optional) OpenWeatherMap API key from https://openweathermap.org/api

---

## Backend Setup

From the repository root:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

Create environment file:

```bash
cp .env.example .env
```

Set values in `.env`:

| Variable | Description |
|---|---|
| `OWM_API_KEY` | OpenWeatherMap API key. Required when `USE_MOCK_DATA=false`. |
| `FLASK_ENV` | `development` or `production`. |
| `FRONTEND_ORIGIN` | Allowed browser origin in production mode. |
| `USE_MOCK_DATA` | `true` to use static mock weather data (no API key needed). |

Run backend:

```bash
python app.py
```

Backend runs at: **http://127.0.0.1:5000**

---

## Frontend Setup

Serve the `frontend/` directory with a local static server.

Example:

```bash
cd frontend
python -m http.server 5500
```

Then open:

- http://127.0.0.1:5500/index.html

> `frontend/js/api.js` is configured to call backend at `http://127.0.0.1:5000/api`.

---

## API Documentation

Base path: `/api`

### `GET /api/weather?city=<name>`
Returns current weather normalized for the UI.

**Validation**
- `city` is required
- `city` length must be <= 100

**Common responses**
- `200` success
- `400` invalid input
- `404` city not found
- `502` upstream/API key/network error

### `GET /api/forecast?city=<name>`
Returns 5-day forecast as:

```json
{
  "forecast": [
    {
      "dt": 1716292800,
      "temp_max": 18,
      "temp_min": 11,
      "description": "light rain",
      "icon": "10d"
    }
  ]
}
```

**Validation/Errors** follow the same pattern as `/weather`.

### `GET /api/geocode?lat=<float>&lon=<float>`
Reverse-geocodes coordinates to city name.

**Validation**
- `lat` and `lon` are required
- both must be numeric
- latitude range: `-90..90`
- longitude range: `-180..180`

**Response example**

```json
{ "city": "London" }
```

---

## Development Notes

- CORS behavior in `backend/app.py`:
  - Development (`FLASK_ENV=development`): all origins allowed (`*`)
  - Production: restricted by `FRONTEND_ORIGIN`
- Global rate limit is configured via Flask-Limiter (`60 per minute` by default).
- Cache is currently in-memory `SimpleCache` with 10-minute default timeout.
- Forecast data is reduced from OWM 3-hour intervals to one representative slot per day (closest to noon UTC).

---

## Testing

From `backend/`:

```bash
python -m pytest
```

If `pytest` is not installed, install it first:

```bash
pip install pytest
```

---

## Troubleshooting

- **`OWM_API_KEY is not set`**: add key to `backend/.env` or set `USE_MOCK_DATA=true`.
- **CORS errors in browser**: confirm backend is running and `FRONTEND_ORIGIN` is correct for production mode.
- **Frontend cannot fetch API**: ensure backend is on `http://127.0.0.1:5000` and frontend is served (not opened as raw `file://` in strict browser setups).

---

## License

No license file is currently included in this repository.
