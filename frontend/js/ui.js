/**
 * ui.js — DOM rendering layer
 * Reads data objects returned by api.js and updates the page.
 * No fetch calls here; no business logic in api.js.
 */

/* ── Element references ─────────────────────────────────────── */
const els = {
  spinner:         document.getElementById('spinner'),
  weatherResults:  document.getElementById('weatherResults'),
  forecastSection: document.getElementById('forecastSection'),
  forecastCards:   document.getElementById('forecastCards'),
  errorMsg:        document.getElementById('errorMsg'),
  cityName:        document.getElementById('cityName'),
  weatherDate:     document.getElementById('weatherDate'),
  weatherIcon:     document.getElementById('weatherIcon'),
  temperature:     document.getElementById('temperature'),
  tempUnit:        document.querySelector('.temp-unit'),
  weatherDesc:     document.getElementById('weatherDesc'),
  feelsLike:       document.getElementById('feelsLike'),
  humidity:        document.getElementById('humidity'),
  windSpeed:       document.getElementById('windSpeed'),
  pressure:        document.getElementById('pressure'),
  visibility:      document.getElementById('visibility'),
  uvIndex:         document.getElementById('uvIndex'),
  sunrise:         document.getElementById('sunrise'),
  sunset:          document.getElementById('sunset'),
};

/* ── Unit state ─────────────────────────────────────────────── */
let currentUnit = 'C';       // 'C' | 'F'
let lastWeatherData = null;  // cache for unit toggling without re-fetch

/* ── Helpers ────────────────────────────────────────────────── */

function celsiusToFahrenheit(c) {
  return Math.round((c * 9) / 5 + 32);
}

function formatTemp(celsius) {
  return currentUnit === 'C' ? Math.round(celsius) : celsiusToFahrenheit(celsius);
}

function formatTime(unixSeconds, timezoneOffsetSeconds) {
  const date = new Date((unixSeconds + timezoneOffsetSeconds) * 1000);
  const h = String(date.getUTCHours()).padStart(2, '0');
  const m = String(date.getUTCMinutes()).padStart(2, '0');
  return `${h}:${m}`;
}

function shortDay(unixSeconds) {
  return new Date(unixSeconds * 1000).toLocaleDateString('en-US', { weekday: 'short' });
}

function iconUrl(code) {
  return `https://openweathermap.org/img/wn/${code}@2x.png`;
}

/* ── Spinner ────────────────────────────────────────────────── */

function showSpinner() {
  els.spinner.hidden = false;
  els.weatherResults.hidden = true;
  els.forecastSection.hidden = true;
  hideError();
}

function hideSpinner() {
  els.spinner.hidden = true;
}

/* ── Error ──────────────────────────────────────────────────── */

function showError(message) {
  els.errorMsg.textContent = message;
  els.errorMsg.hidden = false;
}

function hideError() {
  els.errorMsg.hidden = true;
  els.errorMsg.textContent = '';
}

/* ── Current Weather ────────────────────────────────────────── */

/**
 * Render the current weather card from a Flask /api/weather response.
 * Expected shape:
 * {
 *   city, country, dt, timezone,
 *   temp, feels_like, humidity, wind_speed,
 *   pressure, visibility, uv_index,
 *   description, icon,
 *   sunrise, sunset
 * }
 * @param {Object} data
 */
function renderWeather(data) {
  lastWeatherData = data;

  const unitLabel = currentUnit === 'C' ? '°C' : '°F';

  els.cityName.textContent    = `${data.city}, ${data.country}`;
  els.weatherDate.textContent = new Date(data.dt * 1000).toLocaleDateString('en-US', {
    weekday: 'long', year: 'numeric', month: 'long', day: 'numeric',
  });

  els.weatherIcon.src = iconUrl(data.icon);
  els.weatherIcon.alt = data.description;

  els.temperature.textContent = formatTemp(data.temp);
  els.tempUnit.textContent    = unitLabel;
  els.weatherDesc.textContent = data.description;

  els.feelsLike.textContent = `${formatTemp(data.feels_like)}${unitLabel}`;
  els.humidity.textContent  = `${data.humidity}%`;
  els.windSpeed.textContent = `${data.wind_speed} m/s`;
  els.pressure.textContent  = `${data.pressure} hPa`;
  els.visibility.textContent = `${(data.visibility / 1000).toFixed(1)} km`;
  els.uvIndex.textContent   = data.uv_index ?? '—';

  els.sunrise.textContent = formatTime(data.sunrise, data.timezone);
  els.sunset.textContent  = formatTime(data.sunset,  data.timezone);

  els.weatherResults.hidden = false;
}

/* ── Forecast ───────────────────────────────────────────────── */

/**
 * Render the 5-day forecast strip from a Flask /api/forecast response.
 * Expected shape: { forecast: [ { dt, temp_max, temp_min, description, icon }, ... ] }
 * @param {Object} data
 */
function renderForecast(data) {
  const unitLabel = currentUnit === 'C' ? '°C' : '°F';
  els.forecastCards.innerHTML = '';

  data.forecast.forEach((day) => {
    const card = document.createElement('div');
    card.className = 'forecast-card';
    card.innerHTML = `
      <span class="forecast-card__day">${shortDay(day.dt)}</span>
      <img class="forecast-card__icon" src="${iconUrl(day.icon)}" alt="${day.description}" />
      <span class="forecast-card__temp-max">${formatTemp(day.temp_max)}${unitLabel}</span>
      <span class="forecast-card__temp-min">${formatTemp(day.temp_min)}${unitLabel}</span>
      <span class="forecast-card__desc">${day.description}</span>
    `;
    els.forecastCards.appendChild(card);
  });

  els.forecastSection.hidden = false;
}

/* ── Unit Toggle ────────────────────────────────────────────── */

/**
 * Switch displayed unit and re-render cached data (no extra fetch needed).
 * @param {'C'|'F'} unit
 */
function setUnit(unit) {
  currentUnit = unit;

  document.getElementById('celsiusBtn').classList.toggle('active', unit === 'C');
  document.getElementById('fahrenheitBtn').classList.toggle('active', unit === 'F');
  document.getElementById('celsiusBtn').setAttribute('aria-pressed', unit === 'C');
  document.getElementById('fahrenheitBtn').setAttribute('aria-pressed', unit === 'F');

  if (lastWeatherData) {
    renderWeather(lastWeatherData);
  }
}
