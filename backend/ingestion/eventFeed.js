/**
 * Event Feed Ingestion Module
 * Tracks upcoming concerts, matches, stadium events, and roadwork hazards per zone.
 */

const activeEventsList = [
  {
    eventId: "EVT-88",
    name: "Stadium Sports Championship",
    zone: "Central Zone",
    impactScore: 0.85,
    expectedDispersal: "06:00 PM",
    attendance: 25000
  },
  {
    eventId: "EVT-89",
    name: "East Commercial Roadwork Maintenance",
    zone: "East Commercial",
    impactScore: 0.60,
    expectedDispersal: "Continuous",
    attendance: 0
  },
  {
    eventId: "EVT-90",
    name: "Metro Medical Priority Transport",
    zone: "South District",
    impactScore: 0.95,
    expectedDispersal: "Active Green Corridor",
    attendance: 0
  }
];

/**
 * Returns active events affecting a specific zone
 */
function getEventFeed(zone) {
  const events = activeEventsList.filter(evt => evt.zone === zone);
  const totalImpact = events.reduce((acc, evt) => Math.max(acc, evt.impactScore), 0);
  
  return {
    activeEvents: events.map(e => e.name),
    eventScore: parseFloat(totalImpact.toFixed(2))
  };
}

module.exports = {
  getEventFeed,
  activeEventsList
};
