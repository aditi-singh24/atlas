/**
 * Weather API Feed Ingestion Module
 * Ingests live weather from OpenWeatherMap API (Bangalore, India)
 */

const OPENWEATHER_KEY = process.env.OPENWEATHERMAP_API_KEY;
const BANGALORE_LAT = 12.9716;
const BANGALORE_LNG = 77.5946;

/**
 * Maps OpenWeatherMap condition codes to congestion impact scores
 */
function getImpactScore(weatherDescription, clouds) {
  const desc = weatherDescription.toLowerCase();
  
  if (desc.includes('thunderstorm') || desc.includes('heavy rain')) {
    return 0.90; // Storm Hazard
  } else if (desc.includes('rain') || desc.includes('drizzle')) {
    return 0.70; // Moderate Rain
  } else if (desc.includes('cloud')) {
    return 0.35; // Overcast
  }
  return 0.10; // Clear
}

/**
 * Fetches live weather from OpenWeatherMap
 */
async function getWeatherFeed(zone = null) {
  try {
    if (!OPENWEATHER_KEY) {
      throw new Error('OPENWEATHERMAP_API_KEY not set in .env');
    }

    const url = `https://api.openweathermap.org/data/2.5/weather?lat=${BANGALORE_LAT}&lon=${BANGALORE_LNG}&units=metric&appid=${OPENWEATHER_KEY}`;
    const response = await fetch(url);

    if (!response.ok) {
      throw new Error(`OpenWeatherMap API error: ${response.status}`);
    }

    const data = await response.json();
    const weatherMain = data.weather[0].main;
    const weatherDesc = data.weather[0].description;
    const temp = data.main.temp;
    const humidity = data.main.humidity;
    const windSpeed = data.wind.speed;

    const impactScore = getImpactScore(weatherDesc, data.clouds.all);

    return {
      condition: weatherMain,
      description: weatherDesc,
      temperature: temp,
      humidity: humidity,
      windSpeed: windSpeed,
      impactScore: parseFloat(impactScore.toFixed(2)),
      text: `${weatherMain} (${temp}°C) - Impact: ${Math.round(impactScore * 100)}%`,
      timestamp: new Date().toISOString()
    };
  } catch (error) {
    console.error('[Weather Feed Error]:', error.message);
    // Fallback to simulated data if API fails
    return {
      condition: "API Unavailable",
      description: "Using cached forecast",
      temperature: 28,
      impactScore: 0.35,
      text: "Weather API temporarily unavailable - using fallback",
      timestamp: new Date().toISOString()
    };
  }
}

module.exports = {
  getWeatherFeed
};