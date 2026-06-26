class IncidentReportRequest {
  final String incidentType;
  final double latitude;
  final double longitude;
  final String description;
  final String? photoUrl;

  IncidentReportRequest({
    required this.incidentType,
    required this.latitude,
    required this.longitude,
    required this.description,
    this.photoUrl,
  });

  Map<String, dynamic> toJson() {
    return {
      'incident_type': incidentType,
      'latitude': latitude,
      'longitude': longitude,
      'description': description,
      'photo_url': photoUrl,
    };
  }
}

class IncidentReportResponse {
  final String referenceCode;
  final String status;

  IncidentReportResponse({
    required this.referenceCode,
    required this.status,
  });

  factory IncidentReportResponse.fromJson(Map<String, dynamic> json) {
    return IncidentReportResponse(
      referenceCode: json['ref_code'] ?? 'UNKNOWN',
      status: json['status'] ?? 'pending',
    );
  }
}