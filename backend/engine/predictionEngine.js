/**
 * ATLAS Multi-Factor Weighted Prediction Engine
 * Integrates Live Traffic, History, Weather, and Event feeds to calculate congestion predictions & alert levels.
 */

const { getLiveTrafficFeed } = require('../ingestion/trafficFeed');
const { getHistoricalFeed } = require('../ingestion/historyFeed');
const { getWeatherFeed } = require('../ingestion/weatherFeed');
const { getEventFeed } = require('../ingestion/eventFeed');

/**
 * Calculates alert level based on predicted congestion score
 */
function getAlertLevel(score) {
  if (score >= 85) return 'SEVERE';
  if (score >= 65) return 'HIGH';
  if (score >= 40) return 'MEDIUM';
  return 'LOW';
}

/**
 * Generates PredictionOutput objects for all monitored road segments
 */
async function generatePredictions() {
  try {
    const liveTraffic = await getLiveTrafficFeed();
    const weather = await getWeatherFeed(); // Global weather for all zones

    const predictions = await Promise.all(liveTraffic.map(async (segment) => {
      const history = getHistoricalFeed(segment.segmentId);
      const events = await getEventFeed(segment.zone);

      // Weighted multi-factor model
      const liveScore = segment.liveScore; // 0.0 - 1.0
      const historyScore = history.historyScore; // 0.0 - 1.0
      const weatherScore = weather.impactScore; // 0.0 - 1.0
      const eventScore = events.eventScore; // 0.0 - 1.0

      const weightedScore = (liveScore * 0.40) + (historyScore * 0.25) + (weatherScore * 0.15) + (eventScore * 0.20);
      const predictedCongestion = Math.min(100, Math.round(weightedScore * 100));
      const alertLevel = getAlertLevel(predictedCongestion);

      return {
        segmentId: segment.segmentId,
        segmentName: segment.segmentName,
        zone: segment.zone,
        currentCongestion: segment.densityPercent,
        predictedCongestion: predictedCongestion,
        alertLevel: alertLevel,
        predictedInMinutes: Math.round(15 + Math.random() * 10), // Forecast horizon (15-25m ahead)
        factors: {
          liveScore: liveScore,
          historyScore: historyScore,
          weatherScore: weatherScore,
          eventScore: eventScore
        },
        weatherCondition: weather.condition,
        activeEvents: events.activeEvents,
        timestamp: new Date().toISOString()
      };
    }));

    return predictions;
  } catch (error) {
    console.error('[Prediction Engine Error]:', error.message);
    throw error;
  }
}

module.exports = {
  generatePredictions,
  getAlertLevel
};