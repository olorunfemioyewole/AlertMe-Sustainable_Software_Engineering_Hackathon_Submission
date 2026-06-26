import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:geolocator/geolocator.dart';
import '../services/api_client.dart';
import '../models/incident_report.dart';
import '../theme.dart';
import 'success_screen.dart';

class ReportScreen extends ConsumerStatefulWidget {
  const ReportScreen({super.key});

  @override
  ConsumerState<ReportScreen> createState() => _ReportScreenState();
}

class _ReportScreenState extends ConsumerState<ReportScreen> {
  final _formKey = GlobalKey<FormState>();
  String? _selectedType;
  final _locationController = TextEditingController();
  bool _isLoading = false;
  String? _errorMessage;

  final List<String> _incidentTypes = [
    'Armed Robbery',
    'Kidnapping',
    'Communal Violence',
    'Insurgency',
    'Suspicious Activity',
    'Medical Emergency'
  ];

  Future<Position?> _getCurrentLocation() async {
    bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
    if (!serviceEnabled) return null;

    LocationPermission permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.denied) return null;
    }

    if (permission == LocationPermission.deniedForever) return null;
    return await Geolocator.getCurrentPosition(desiredAccuracy: LocationAccuracy.high);
  }

  Future<void> _submitReport() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final position = await _getCurrentLocation();
      final lat = position?.latitude ?? 6.5244; // Fallback to Lagos defaults if blocked
      final lng = position?.longitude ?? 3.3792;

      final dio = ref.read(apiClientProvider);

      final reportData = IncidentReportRequest(
        incidentType: _selectedType!,
        location: _locationController.text.trim(),
        latitude: lat,
        longitude: lng,
        phoneOrUserId: '+2348012345678', // Placeholder matching test profile limits
      );

      // Hit FastAPI mobile_api gateway incident router
      final response = await dio.post('/incidents/report', data: reportData.toJson());

      if (mounted) {
        final parsedResponse = IncidentReportResponse.fromJson(response.data);
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => SuccessScreen(referenceCode: parsedResponse.referenceCode),
          ),
        );
        // Clear form on success
        _locationController.clear();
        setState(() => _selectedType = null);
      }
    } on DioException catch (e) {
      setState(() {
        _errorMessage = e.response?.data['detail'] ?? 'Submission limited or connection timed out.';
      });
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Report Incident', style: TextStyle(color: AppTheme.text, fontWeight: FontWeight.w600)),
        backgroundColor: AppTheme.background,
        elevation: 0,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Emergency Type', style: TextStyle(color: AppTheme.text, fontWeight: FontWeight.w600, fontSize: 14)),
              const SizedBox(height: 8),
              DropdownButtonFormField<String>(
                value: _selectedType,
                hint: const Text('Select anomaly category'),
                decoration: const InputDecoration(),
                items: _incidentTypes.map((type) {
                  return DropdownMenuItem(value: type, child: Text(type));
                }).toList(),
                onChanged: (val) => setState(() => _selectedType = val),
                validator: (val) => val == null ? 'Field required' : null,
              ),
              const SizedBox(height: 20),
              Text('Area / Landmark / LGA Description', style: TextStyle(color: AppTheme.text, fontWeight: FontWeight.w600, fontSize: 14)),
              const SizedBox(height: 8),
              TextFormField(
                controller: _locationController,
                decoration: const InputDecoration(hintText: 'e.g. Yaba Market, Lagos'),
                validator: (val) => val == null || val.isEmpty ? 'Field required' : null,
              ),
              const SizedBox(height: 32),
              if (_errorMessage != null) ...[
                Text(_errorMessage!, style: const TextStyle(color: AppTheme.error)),
                const SizedBox(height: 12),
              ],
              ElevatedButton(
                onPressed: _isLoading ? null : _submitReport,
                style: ElevatedButton.styleFrom(backgroundColor: AppTheme.primary),
                child: _isLoading
                    ? const SizedBox(height: 24, width: 24, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                    : const Text('Broadcast Alert Now', style: TextStyle(color: Colors.white)),
              ),
            ],
          ),
        ),
      ),
    );
  }
}