/**
 * ATLAS Express Server
 * Delivers REST API endpoints for traffic data ingestion & prediction outputs.
 */

require('dotenv').config();
const express = require('express');
const cors = require('cors');
const { generatePredictions } = require('./engine/predictionEngine');
const { getLiveTrafficFeed } = require('./ingestion/trafficFeed');
const { getActiveEventsList } = require('./ingestion/eventFeed');

const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors());
app.use(express.json());

// Health Check
app.get('/api/health', (req, res) => {
  res.json({
    status: 'OK',
    system: 'ATLAS AI Traffic Logistics & Adaptive System',
    codename: 'CIPHER',
    timestamp: new Date().toISOString()
  });
});

/**
 * Deliverable Endpoint: GET /api/predictions
 * Returns array of PredictionOutput objects across monitored road segments
 */
app.get('/api/predictions', async (req, res) => {
  try {
    const predictions = await generatePredictions();
    res.json(predictions);
  } catch (error) {
    res.status(500).json({ error: 'Failed to compute predictions', message: error.message });
  }
});

/**
 * Endpoint: GET /api/predictions/:segmentId
 * Returns prediction detail for a specific segment
 */
app.get('/api/predictions/:segmentId', async (req, res) => {
  try {
    const { segmentId } = req.params;
    const predictions = await generatePredictions();
    const prediction = predictions.find(p => p.segmentId.toUpperCase() === segmentId.toUpperCase());

    if (!prediction) {
      return res.status(404).json({ error: `Segment '${segmentId}' not found` });
    }

    res.json(prediction);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch prediction', message: error.message });
  }
});

/**
 * Endpoint: GET /api/ingestion/summary
 * Returns raw ingestion signal feeds (Traffic, Events, System status)
 */
app.get('/api/ingestion/summary', async (req, res) => {
  try {
    const liveTraffic = await getLiveTrafficFeed();
    const activeEvents = await getActiveEventsList();
    
    res.json({
      liveTraffic,
      activeEvents,
      totalSegmentsMonitored: 5,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(500).json({ 
      error: 'Failed to fetch ingestion summary', 
      message: error.message 
    });
  }
});

// Start Server
app.listen(PORT, () => {
  console.log(`=======================================================`);
  console.log(`ATLAS Backend Server Running on http://localhost:${PORT}`);
  console.log(`Deliverable Endpoint: GET http://localhost:${PORT}/api/predictions`);
  console.log(`=======================================================`);
});