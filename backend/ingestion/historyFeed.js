/**
 * Historical Traffic Data Ingestion Module
 * Provides baseline congestion patterns based on day-of-week and time-of-day history.
 */

const historicalBaselines = {
  "SEG-101": { historicalAvgDensity: 75, sameDayLastWeekDensity: 74, peakHourRisk: 0.85 },
  "SEG-102": { historicalAvgDensity: 40, sameDayLastWeekDensity: 38, peakHourRisk: 0.42 },
  "SEG-103": { historicalAvgDensity: 58, sameDayLastWeekDensity: 60, peakHourRisk: 0.65 },
  "SEG-104": { historicalAvgDensity: 30, sameDayLastWeekDensity: 28, peakHourRisk: 0.32 },
  "SEG-105": { historicalAvgDensity: 82, sameDayLastWeekDensity: 80, peakHourRisk: 0.88 }
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
