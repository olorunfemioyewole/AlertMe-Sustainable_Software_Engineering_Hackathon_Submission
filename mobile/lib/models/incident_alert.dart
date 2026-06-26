class IncidentAlert {
  final String referenceCode;
  final String incidentType;
  final String location;
  final int score;
  final int tier;
  final String status;
  final DateTime timestamp;

  IncidentAlert({
    required this.referenceCode,
    required this.incidentType,
    required this.location,
    required this.score,
    required this.tier,
    required this.status,
    required this.timestamp,
  });

  factory IncidentAlert.fromJson(Map<String, dynamic> json) {
    return IncidentAlert(
      referenceCode: json['ref'] ?? json['reference_code'] ?? 'UNKNOWN',
      incidentType: json['incident_type'] ?? 'General Incident',
      location: json['location'] ?? 'Unknown Location',
      score: json['score'] ?? 0,
      tier: json['tier'] ?? 1,
      status: json['status'] ?? 'pending',
      timestamp: json['timestamp'] != null
          ? DateTime.parse(json['timestamp'])
          : DateTime.now(),
    );
  }
}