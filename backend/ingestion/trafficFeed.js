/**
 * Live Traffic Feed Ingestion Module
 * Simulates real-time telemetry from cameras and road sensors (speed, density, volume).
 */

const roadSegments = [
  {
    segmentId: "SEG-101",
    segmentName: "Central Ave & 5th St",
    zone: "Central Zone",
    speedLimitKmH: 50,
    currentSpeedKmH: 22,
    densityPercent: 78,
    vehicleCountPerHour: 1840
  },
  {
    segmentId: "SEG-102",
    segmentName: "North Highway Junction 4",
    zone: "North Corridor",
    speedLimitKmH: 80,
    currentSpeedKmH: 72,
    densityPercent: 35,
    vehicleCountPerHour: 1100
  },
  {
    segmentId: "SEG-103",
    segmentName: "East Commercial Blvd",
    zone: "East Commercial",
    speedLimitKmH: 60,
    currentSpeedKmH: 34,
    densityPercent: 62,
    vehicleCountPerHour: 1450
  },
  {
    segmentId: "SEG-104",
    segmentName: "West Bypass Interchange",
    zone: "West Zone",
    speedLimitKmH: 70,
    currentSpeedKmH: 65,
    densityPercent: 28,
    vehicleCountPerHour: 920
  },
  {
    segmentId: "SEG-105",
    segmentName: "South Medical Center Way",
    zone: "South District",
    speedLimitKmH: 45,
    currentSpeedKmH: 18,
    densityPercent: 88,
    vehicleCountPerHour: 2100
  }
];

/**
 * Returns current live traffic signals per segment
 */
function getLiveTrafficFeed() {
  // Add slight dynamic noise to simulate real-time sensor updates
  return roadSegments.map(segment => {
    const noise = (Math.random() - 0.5) * 4;
    const currentDensity = Math.min(100, Math.max(10, Math.round(segment.densityPercent + noise)));
    const liveScore = currentDensity / 100;

    return {
      ...segment,
      densityPercent: currentDensity,
      liveScore: parseFloat(liveScore.toFixed(2))
    };
  });
}

module.exports = {
  getLiveTrafficFeed
};
