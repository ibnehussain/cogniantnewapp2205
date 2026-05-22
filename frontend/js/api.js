/**
 * api.js — Flask backend communication layer
 * All fetch calls go through this module. The backend keeps the OWM API key
 * server-side; the browser only talks to /api/*.
 */

const API_BASE = 'http://127.0.0.1:5000/api';

/**
 * Fetch current weather for a city name.
 * @param {string} city
 * @returns {Promise<Object>} Parsed JSON from Flask /api/weather
 */
async function fetchWeather(city) {
  const params = new URLSearchParams({ city: city.trim() });
  const response = await fetch(`${API_BASE}/weather?${params}`);

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.error || `Request failed (${response.status})`);
  }

  return response.json();
}

/**
 * Fetch 5-day forecast for a city name.
 * @param {string} city
 * @returns {Promise<Object>} Parsed JSON from Flask /api/forecast
 */
async function fetchForecast(city) {
  const params = new URLSearchParams({ city: city.trim() });
  const response = await fetch(`${API_BASE}/forecast?${params}`);

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.error || `Forecast request failed (${response.status})`);
  }

  return response.json();
}

/**
 * Reverse-geocode coordinates to a city name via Flask /api/geocode.
 * @param {number} lat
 * @param {number} lon
 * @returns {Promise<string>} City name string
 */
async function fetchCityFromCoords(lat, lon) {
  const params = new URLSearchParams({ lat, lon });
  const response = await fetch(`${API_BASE}/geocode?${params}`);

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.error || 'Could not resolve location');
  }

  const data = await response.json();
  return data.city;
}
