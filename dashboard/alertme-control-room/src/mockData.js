export const initialIncidents = [
  {
    id: "ALT-20260626-4190",
    type: "Armed Robbery",
    locationName: "Yaba, Lagos",
    coordinates: "6.5139, 3.3970",
    timeAgo: "2 mins ago",
    timestamp: new Date(Date.now() - 120000).toISOString(),
    status: "Under Review",
    description: "Observed unusual movement near the main bypass corridor.",
    credibilityWeight: "1.0",
    source: "Mobile app"
  },
  {
    id: "ALT-20260626-3022",
    type: "Kidnapping",
    locationName: "Ikeja, Lagos",
    coordinates: "6.6018, 3.3515",
    timeAgo: "15 mins ago",
    timestamp: new Date(Date.now() - 900000).toISOString(),
    status: "Verified",
    description: "Unidentified vehicle forced cross-interaction on minor service lane.",
    credibilityWeight: "1.0",
    source: "Mobile app"
  },
  {
    id: "ALT-20260626-1088",
    type: "Insurgency / Banditry",
    locationName: "Kaduna Bypass corridor",
    coordinates: "10.5105, 7.4168",
    timeAgo: "1 hour ago",
    timestamp: new Date(Date.now() - 3600000).toISOString(),
    status: "Dispatched",
    description: "Early morning tactical checkpoint breach reports incoming.",
    credibilityWeight: "0.8",
    source: "USSD service Gateway"
  }
];