/**
 * Historical Traffic Data Ingestion Module
 * Provides baseline congestion patterns based on day-of-week and time-of-day history.
 *
 * Kept simulated intentionally — there is no public dataset for per-junction
 * historical congestion in Bangalore. Baselines below are set from each
 * junction's well-documented real-world reputation (Silk Board is
 * consistently ranked the worst bottleneck in the city, etc.), not
 * randomly picked.
 */

const historicalBaselines = {
  "SEG-101": { historicalAvgDensity: 88, sameDayLastWeekDensity: 86, peakHourRisk: 0.92 }, // Silk Board Junction
  "SEG-102": { historicalAvgDensity: 76, sameDayLastWeekDensity: 74, peakHourRisk: 0.80 }, // Marathahalli Bridge
  "SEG-103": { historicalAvgDensity: 65, sameDayLastWeekDensity: 63, peakHourRisk: 0.70 }, // Hebbal Flyover
  "SEG-104": { historicalAvgDensity: 78, sameDayLastWeekDensity: 77, peakHourRisk: 0.82 }, // KR Puram Junction
  "SEG-105": { historicalAvgDensity: 80, sameDayLastWeekDensity: 79, peakHourRisk: 0.85 }  // Tin Factory Junction
};

/**
 * Returns historical congestion score for a segment ID
 */
function getHistoricalFeed(segmentId) {
  const data = historicalBaselines[segmentId] || { historicalAvgDensity: 50, peakHourRisk: 0.50 };
  const historyScore = data.historicalAvgDensity / 100;
  return {
    ...data,
    historyScore: parseFloat(historyScore.toFixed(2))
  };
}

module.exports = {
  getHistoricalFeed
};