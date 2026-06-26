import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../services/api_client.dart';

class AuthState {
  final bool isAuthenticated;
  final bool isLoading;
  final String? errorMessage;

  AuthState({this.isAuthenticated = false, this.isLoading = false, this.errorMessage});

  AuthState copyWith({bool? isAuthenticated, bool? isLoading, String? errorMessage}) {
    return AuthState(
      isAuthenticated: isAuthenticated ?? this.isAuthenticated,
      isLoading: isLoading ?? this.isLoading,
      errorMessage: errorMessage,
    );
  }
}

class AuthNotifier extends StateNotifier<AuthState> {
  final Dio _dio;
  final _storage = const FlutterSecureStorage();

  AuthNotifier(this._dio) : super(AuthState()) {
    _checkToken();
  }

  void _checkToken() async {
    final token = await _storage.read(key: 'jwt_token');
    if (token != null) {
      state = AuthState(isAuthenticated: true);
    }
  }

  Future<void> register(String email, String phoneNumber, String password) async {
    state = state.copyWith(isLoading: true);
    try {
      final response = await _dio.post('/auth/register', data: {
        'email': email,
        'phone_number': phoneNumber,
        'password': password,
      });
      
      final token = response.data['access_token'] ?? response.data['token'];
      if (token != null) {
        await _storage.write(key: 'jwt_token', value: token);
        state = AuthState(isAuthenticated: true);
      }
    } on DioException catch (e) {
      state = state.copyWith(
        isLoading: false, 
        errorMessage: e.response?.data['detail'] ?? 'Registration failed',
      );
    }
  }

  Future<void> logout() async {
    await _storage.delete(key: 'jwt_token');
    state = AuthState(isAuthenticated: false);
  }
}

final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  return AuthNotifier(ref.read(apiClientProvider));
});