/**
 * Event Feed Ingestion Module
 * Fetches upcoming events from Ticketmaster Discovery API (Bangalore area)
 */

const TICKETMASTER_KEY = process.env.TICKETMASTER_API_KEY;
const BANGALORE_LAT = 12.9716;
const BANGALORE_LNG = 77.5946;
const SEARCH_RADIUS_KM = 25; // Search within 25km of central Bangalore

// Cache for events to reduce API calls
let cachedEvents = [];
let cacheTimestamp = 0;
const CACHE_DURATION_MS = 30 * 60 * 1000; // 30 minutes

/**
 * Maps event classifications to congestion impact scores
 */
function getImpactScore(eventType, attendance = 0) {
  const type = eventType.toLowerCase();
  
  if (type.includes('festival') || type.includes('concert') || attendance > 10000) {
    return 0.85;
  } else if (type.includes('sports') || type.includes('match')) {
    return 0.80;
  } else if (type.includes('conference') || type.includes('fair')) {
    return 0.60;
  }
  return 0.50;
}

/**
 * Fetches live events from Ticketmaster
 */
async function fetchActiveEvents() {
  try {
    if (!TICKETMASTER_KEY) {
      throw new Error('TICKETMASTER_API_KEY not set in .env');
    }

    // Check cache first
    const now = Date.now();
    if (cachedEvents.length > 0 && (now - cacheTimestamp) < CACHE_DURATION_MS) {
      console.log('[Event Cache Hit]');
      return cachedEvents;
    }

    // Ticketmaster Discovery API endpoint
    const url = new URL('https://app.ticketmaster.com/discovery/v2/events.json');
    url.searchParams.append('apikey', TICKETMASTER_KEY);
    url.searchParams.append('latlong', `${BANGALORE_LAT},${BANGALORE_LNG}`);
    url.searchParams.append('radius', SEARCH_RADIUS_KM);
    url.searchParams.append('size', '10'); // Get top 10 events
    url.searchParams.append('sort', 'date,asc');

    const response = await fetch(url.toString());

    if (!response.ok) {
      throw new Error(`Ticketmaster API error: ${response.status}`);
    }

    const data = await response.json();

    if (data._embedded && data._embedded.events) {
      cachedEvents = data._embedded.events.map((event, idx) => ({
        eventId: `EVT-${100 + idx}`,
        name: event.name,
        zone: "Central Bangalore", // Ticketmaster returns events within radius
        type: event.classifications?.[0]?.segment?.name || "Other",
        impactScore: getImpactScore(event.classifications?.[0]?.segment?.name || "Other", 5000),
        eventDate: event.dates?.start?.dateTime || "TBD",
        venue: event._embedded?.venues?.[0]?.name || "Unknown Venue",
        attendance: 5000, // Estimate
        url: event.url
      }));

      cacheTimestamp = now;
      console.log(`[Events Fetched]: ${cachedEvents.length} events found`);
      return cachedEvents;
    }

    console.warn('[Ticketmaster] No events in response');
    return [];

  } catch (error) {
    console.error('[Event Feed Error]:', error.message);
    // Return cached events even if stale, or empty array
    return cachedEvents;
  }
}

/**
 * Returns active events list (updates from API every 30 minutes)
 */
async function getActiveEventsList() {
  return await fetchActiveEvents();
}

/**
 * Returns events affecting a specific zone with impact score
 */
async function getEventFeed(zone = "Central Bangalore") {
  const allEvents = await fetchActiveEvents();
  const zoneEvents = allEvents.filter(evt => evt.zone.includes(zone) || !zone);
  const maxImpact = zoneEvents.length > 0 
    ? Math.max(...zoneEvents.map(e => e.impactScore))
    : 0;

  return {
    activeEvents: zoneEvents.map(e => e.name),
    eventCount: zoneEvents.length,
    eventScore: parseFloat(maxImpact.toFixed(2)),
    timestamp: new Date().toISOString()
  };
}

module.exports = {
  getEventFeed,
  getActiveEventsList,
  fetchActiveEvents
};