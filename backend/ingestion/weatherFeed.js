/**
 * Weather API Feed Ingestion Module
 * Ingests live weather conditions and calculates congestion impact multiplier.
 */

const weatherConditions = [
  { condition: "Moderate Rain", impactScore: 0.70, text: "Rain - Redirection expected" },
  { condition: "Clear", impactScore: 0.10, text: "Clear Skies" },
  { condition: "Heavy Rain / Thunderstorm", impactScore: 0.90, text: "Storm Hazard" },
  { condition: "Overcast", impactScore: 0.35, text: "Cloudy" }
];

/**
 * Returns current weather conditions and impact score for a zone
 */
function getWeatherFeed(zone) {
  // Simulate weather condition per zone
  if (zone.includes("Central") || zone.includes("East")) {
    return weatherConditions[0]; // Moderate Rain
  } else if (zone.includes("South")) {
    return weatherConditions[2]; // Heavy Rain
  }
  return weatherConditions[1]; // Clear
}

module.exports = {
  getWeatherFeed
};
