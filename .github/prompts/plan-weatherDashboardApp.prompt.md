# Weather Dashboard App — Plan

## Stack
- **Frontend:** HTML + CSS + JavaScript (Fetch API, Geolocation API)
- **Backend:** Python / Flask
- **External API:** OpenWeatherMap (`api.openweathermap.org`)

---

## Functional Requirements

- Display current weather conditions (temperature, humidity, wind speed, description, icon)
- Search weather by city name or ZIP code
- Display a 5-day weather forecast
- Show "feels like" temperature, UV index, visibility, and pressure
- Search bar with submit button and Enter key support
- Toggle between Celsius and Fahrenheit
- Save/bookmark favorite locations (localStorage or backend)
- Display weather for user's current location via Geolocation API
- Render weather icons matching conditions (sunny, rainy, cloudy, etc.)
- Show hourly forecast chart (e.g., Chart.js)
- Display sunrise/sunset times
- Background/theme changes based on weather condition

**Flask API Endpoints:**
- `GET /api/weather?city=<name>` — current weather proxy
- `GET /api/forecast?city=<name>` — multi-day forecast
- `GET /api/geocode?q=<query>` — location resolution
- API key managed server-side only
- Input validation and error handling for bad city names or API failures

---

## Non-Functional Requirements

- Initial page load under 2 seconds
- Weather data response from Flask under 1 second (with caching)
- Cache API responses on the backend (Flask-Caching or Redis, TTL: 10 min)
- API keys stored in `.env` / environment variables, never in frontend code
- Flask validates and sanitizes all query parameters
- CORS policy restricted to the frontend origin
- Rate limiting on Flask endpoints (Flask-Limiter)
- HTTPS in production
- Fully responsive layout (mobile, tablet, desktop) using CSS Grid/Flexbox
- Accessible markup (ARIA labels, sufficient color contrast, keyboard navigable)
- Meaningful error messages for invalid searches or network failures
- Loading spinner/skeleton during data fetch
- Graceful degradation if the third-party weather API is unavailable
- Appropriate HTTP status codes returned (400, 404, 500)
- Environment-based config (development vs production) in Flask
- Frontend JS modularized (separate files for API calls, rendering, UI state)
- `.env` excluded from version control via `.gitignore`
- Flask app deployable with Gunicorn behind Nginx
- Stateless API design for horizontal scaling

---

## User Stories

**US-1: Search Weather by City**
> As a **traveler**, I want to search for current weather by city name so that I can check conditions at my destination before I leave.

Acceptance Criteria:
- Search bar visible on dashboard
- Entering a city name and pressing Enter or clicking Search fetches and displays current weather
- Error message shown if city is not found

---

**US-2: View Multi-Day Forecast**
> As a **daily commuter**, I want to see a 5-day weather forecast so that I can plan my week and decide what to wear or carry.

Acceptance Criteria:
- After searching a city, forecast section displays the next 5 days
- Each day shows min/max temperature, weather icon, and a short description
- Forecast updates whenever a new city is searched

---

**US-3: Use My Current Location**
> As a **casual user**, I want the app to detect my current location automatically so that I don't have to type my city every time I open the dashboard.

Acceptance Criteria:
- "Use My Location" button triggers the browser Geolocation API
- Weather and forecast for the detected location displayed on success
- Clear message shown if location permission is denied

---

**US-4: Toggle Temperature Units**
> As a **user familiar with Fahrenheit**, I want to switch between Celsius and Fahrenheit so that I can read temperatures in the unit I understand best.

Acceptance Criteria:
- A toggle (°C / °F) is always visible on the dashboard
- Switching units instantly updates all displayed temperatures without a new API call
- Selected unit persists for the session

---

## Architecture

```
Frontend (Browser)
├── Dashboard UI (HTML + CSS)
├── app.js (Fetch API / Geolocation)
└── localStorage (favorites, unit preference)
        │
        │  HTTP GET /api/weather?city=London
        ▼
Flask Backend
├── Routes: /api/weather, /api/forecast, /api/geocode
├── Input Validator
├── Rate Limiter (Flask-Limiter)
├── Cache Layer (Flask-Caching, TTL: 10 min)
└── .env (OWM_API_KEY)
        │
        │  GET /data/2.5/weather?q=London&appid=<KEY>
        ▼
OpenWeatherMap API
```

---

## Data Flow

1. User types city name and submits
2. UI shows loading spinner
3. JS sends `GET /api/weather?city=London` to Flask
4. Flask validates and sanitizes input
5. Flask checks cache for "London"
   - **Cache HIT** → return cached JSON immediately
   - **Cache MISS** → call OpenWeatherMap API, store response in cache (TTL: 10 min)
6. Flask transforms raw OWM response, filters to required fields
7. Flask returns clean JSON `{ temp, humidity, wind, icon, ... }` to frontend
8. UI hides spinner, renders weather card and forecast

**Key design decisions:**
- API key lives only on the Flask server — browser never sees it
- Flask transforms the OWM response — frontend is decoupled from OWM's schema
- Cache key = city name, TTL = 10 minutes (balances freshness vs. API quota)

---

## Component Responsibilities

| Layer | Technology | Responsibility |
|---|---|---|
| UI | HTML + CSS | Layout, weather cards, responsive design |
| Client Logic | JavaScript (Fetch API) | API calls, DOM updates, unit toggle, localStorage |
| Backend Routes | Flask (Python) | Request routing, input validation, response shaping |
| Cache | Flask-Caching | Avoid redundant OWM calls, reduce latency |
| Rate Limiter | Flask-Limiter | Prevent abuse of Flask endpoints |
| Secrets | `.env` file | Store OWM API key, never exposed to client |
| External API | OpenWeatherMap | Source of truth for weather data |

---

## Suggested Project Structure

```
weather-dashboard/
├── backend/
│   ├── app.py
│   ├── routes/
│   │   ├── weather.py
│   │   └── forecast.py
│   ├── services/
│   │   └── owm_client.py
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── index.html
│   ├── css/
│   │   └── styles.css
│   └── js/
│       ├── app.js
│       ├── api.js
│       └── ui.js
└── .gitignore
```

---

## Next Steps

- [ ] Scaffold project structure
- [ ] Set up Flask app with `.env` config and CORS
- [ ] Implement `/api/weather` and `/api/forecast` endpoints with caching
- [ ] Build HTML layout and CSS (responsive)
- [ ] Implement `api.js` (fetch wrapper) and `ui.js` (DOM rendering)
- [ ] Add Geolocation support
- [ ] Add °C / °F toggle
- [ ] Add favorites (localStorage)
- [ ] Write unit tests for Flask routes
- [ ] Configure Gunicorn + Nginx for production
