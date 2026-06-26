import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/api_client.dart';
import '../models/incident_alert.dart';

final activeAlertsProvider = FutureProvider<List<IncidentAlert>>((ref) async {
  final dio = ref.read(apiClientProvider);

  try {
    final response = await dio.get('/alerts/active');
    final List data = response.data;
    return data.map((json) => IncidentAlert.fromJson(json)).toList();
  } on DioException catch (e) {
    // If backend returns a 404 or empty stream, map cleanly to an empty list
    if (e.response?.statusCode == 404) return [];
    rethrow;
  }
});