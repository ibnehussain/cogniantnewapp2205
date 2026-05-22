/**
 * app.js — entry point
 * Wires up all user interactions: search, geolocation, unit toggle.
 * Depends on api.js and ui.js being loaded first (see index.html script order).
 */

/* ── Search ─────────────────────────────────────────────────── */

/**
 * Main function: fetch weather + forecast for a city and update the page.
 * @param {string} city
 */
async function getWeatherForCity(city) {
  if (!city || !city.trim()) {
    showError('Please enter a city name.');
    return;
  }

  showSpinner();

  try {
    // Fetch weather and forecast in parallel for speed
    const [weatherData, forecastData] = await Promise.all([
      fetchWeather(city),
      fetchForecast(city),
    ]);

    renderWeather(weatherData);
    renderForecast(forecastData);
  } catch (err) {
    hideSpinner();
    showError(err.message || 'Something went wrong. Please try again.');
  } finally {
    hideSpinner();
  }
}

/* ── Geolocation ─────────────────────────────────────────────── */

function handleGeolocation() {
  if (!navigator.geolocation) {
    showError('Geolocation is not supported by your browser.');
    return;
  }

  showSpinner();

  navigator.geolocation.getCurrentPosition(
    async (position) => {
      try {
        const { latitude, longitude } = position.coords;
        const city = await fetchCityFromCoords(latitude, longitude);
        document.getElementById('cityInput').value = city;
        await getWeatherForCity(city);
      } catch (err) {
        hideSpinner();
        showError(err.message || 'Could not fetch weather for your location.');
      }
    },
    (err) => {
      hideSpinner();
      const messages = {
        1: 'Location access denied. Please allow location permission.',
        2: 'Location unavailable. Try searching by city name.',
        3: 'Location request timed out. Try again.',
      };
      showError(messages[err.code] || 'Could not get your location.');
    },
    { timeout: 10000 }
  );
}

/* ── Event Listeners ─────────────────────────────────────────── */

document.addEventListener('DOMContentLoaded', () => {

  const cityInput    = document.getElementById('cityInput');
  const getWeatherBtn = document.getElementById('getWeatherBtn');
  const locationBtn  = document.getElementById('locationBtn');
  const celsiusBtn   = document.getElementById('celsiusBtn');
  const fahrenheitBtn = document.getElementById('fahrenheitBtn');

  // Search button click
  getWeatherBtn.addEventListener('click', () => {
    getWeatherForCity(cityInput.value);
  });

  // Enter key in search input
  cityInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      getWeatherForCity(cityInput.value);
    }
  });

  // Geolocation button
  locationBtn.addEventListener('click', handleGeolocation);

  // Unit toggle
  celsiusBtn.addEventListener('click', () => setUnit('C'));
  fahrenheitBtn.addEventListener('click', () => setUnit('F'));

});
