/**
 * Live Traffic Feed Ingestion Module
 * Fetches real-time traffic data from TomTom Traffic Flow API (Bangalore, India)
 */

const TOMTOM_KEY = process.env.TOMTOM_API_KEY;

/**
 * Real Bangalore traffic hotspots (lat, lng)
 */
const bangaloreSegments = [
  {
    segmentId: "SEG-101",
    segmentName: "Silk Board Junction",
    zone: "Central Zone",
    lat: 12.9352,
    lng: 77.6245,
    speedLimitKmH: 50
  },
  {
    segmentId: "SEG-102",
    segmentName: "Marathahalli Bridge",
    zone: "East Zone",
    lat: 12.9698,
    lng: 77.7499,
    speedLimitKmH: 80
  },
  {
    segmentId: "SEG-103",
    segmentName: "Hebbal Junction",
    zone: "North Zone",
    lat: 13.0109,
    lng: 77.5904,
    speedLimitKmH: 60
  },
  {
    segmentId: "SEG-104",
    segmentName: "KR Puram Junction",
    zone: "East Commercial",
    lat: 13.0277,
    lng: 77.6408,
    speedLimitKmH: 70
  },
  {
    segmentId: "SEG-105",
    segmentName: "Whitefield Junction",
    zone: "North Corridor",
    lat: 12.9698,
    lng: 77.7480,
    speedLimitKmH: 45
  }
];

/**
 * Fetches live traffic data from TomTom for a specific coordinate
 */
async function getTrafficForSegment(segment) {
  try {
    if (!TOMTOM_KEY) {
      throw new Error('TOMTOM_API_KEY not set in .env');
    }

    // TomTom Traffic Flow API endpoint
    const url = `https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json?point=${segment.lat},${segment.lng}&key=${TOMTOM_KEY}`;
    
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error(`TomTom API error: ${response.status}`);
    }

    const data = await response.json();
    
    if (data.flowSegmentData) {
      const flow = data.flowSegmentData;
      const currentSpeedKmH = flow.currentSpeed;
      const freeFlowSpeedKmH = flow.freeFlowSpeed;
      const densityPercent = Math.round((1 - currentSpeedKmH / freeFlowSpeedKmH) * 100);
      
      return {
        ...segment,
        currentSpeedKmH: Math.round(currentSpeedKmH),
        densityPercent: Math.min(100, Math.max(0, densityPercent)),
        liveScore: parseFloat((densityPercent / 100).toFixed(2)),
        vehicleCountPerHour: Math.round(flow.currentFlow || 1000),
        timestamp: new Date().toISOString()
      };
    }

    throw new Error('No flow segment data returned');

  } catch (error) {
    console.warn(`[Traffic API Error for ${segment.segmentName}]:`, error.message);
    // Return cached/simulated data as fallback
    const noise = (Math.random() - 0.5) * 10;
    const baseDensity = Math.random() * 70 + 20;
    const density = Math.min(100, Math.max(10, Math.round(baseDensity + noise)));
    
    return {
      ...segment,
      currentSpeedKmH: Math.round(segment.speedLimitKmH * (1 - density / 200)),
      densityPercent: density,
      liveScore: parseFloat((density / 100).toFixed(2)),
      vehicleCountPerHour: Math.round(1500 + Math.random() * 1000),
      timestamp: new Date().toISOString(),
      source: 'fallback'
    };
  }
}

/**
 * Returns current live traffic for all segments
 */
async function getLiveTrafficFeed() {
  try {
    const trafficPromises = bangaloreSegments.map(seg => getTrafficForSegment(seg));
    const allTraffic = await Promise.all(trafficPromises);
    return allTraffic;
  } catch (error) {
    console.error('[Traffic Feed Fatal Error]:', error.message);
    return bangaloreSegments.map(seg => ({
      ...seg,
      currentSpeedKmH: 30,
      densityPercent: 60,
      liveScore: 0.60,
      vehicleCountPerHour: 1500,
      timestamp: new Date().toISOString(),
      source: 'fallback'
    }));
  }
}

module.exports = {
  getLiveTrafficFeed,
  bangaloreSegments
};