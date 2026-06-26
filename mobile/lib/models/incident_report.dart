class IncidentReportRequest {
  final String incidentType;
  final String location;
  final double latitude;
  final double longitude;
  final String phoneOrUserId;
  final String email; // Temporary workaround parameter
  final String source;
  final bool isVerifiedReporter;

  IncidentReportRequest({
    required this.incidentType,
    required this.location,
    required this.latitude,
    required this.longitude,
    required this.phoneOrUserId,
    this.email = 'test@example.com', // Hardcoded fallback value requested
    this.source = 'app',
    this.isVerifiedReporter = false,
  });

  Map<String, dynamic> toJson() {
    return {
      'incident_type': incidentType,
      'location': location,
      'latitude': latitude,
      'longitude': longitude,
      'phone_or_user_id': phoneOrUserId,
      'email': email,
      'source': source,
      'is_verified_reporter': isVerifiedReporter,
    };
  }
}

class IncidentReportResponse {
  final String referenceCode;
  final String tier;
  final String status;

  IncidentReportResponse({
    required this.referenceCode,
    required this.tier,
    required this.status,
  });

  factory IncidentReportResponse.fromJson(Map<String, dynamic> json) {
    return IncidentReportResponse(
      // Handles 'ref' mapping directly from FastAPI response payload structure
      referenceCode: json['ref'] ?? json['reference_code'] ?? 'UNKNOWN',
      tier: json['tier']?.toString() ?? '1',
      status: json['status'] ?? 'pending',
    );
  }
}