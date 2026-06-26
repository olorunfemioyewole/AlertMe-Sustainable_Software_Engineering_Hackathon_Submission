import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../services/api_client.dart';

class AuthState {
  final bool isAuthenticated;
  final bool isLoading;
  final String? errorMessage;
  // Dynamic fields to hold the authenticated session information
  final String? email;
  final String? phoneNumber;

  AuthState({
    this.isAuthenticated = false,
    this.isLoading = false,
    this.errorMessage,
    this.email,
    this.phoneNumber,
  });

  AuthState copyWith({
    bool? isAuthenticated,
    bool? isLoading,
    String? errorMessage,
    String? email,
    String? phoneNumber,
  }) {
    return AuthState(
      isAuthenticated: isAuthenticated ?? this.isAuthenticated,
      isLoading: isLoading ?? this.isLoading,
      errorMessage: errorMessage,
      email: email ?? this.email,
      phoneNumber: phoneNumber ?? this.phoneNumber,
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
    final email = await _storage.read(key: 'session_email');
    final phone = await _storage.read(key: 'session_phone');

    if (token != null) {
      state = AuthState(
        isAuthenticated: true,
        email: email,
        phoneNumber: phone,
      );
    }
  }

  Future<void> login(String email, String password) async {
    state = state.copyWith(isLoading: true);
    try {
      final response = await _dio.post('/auth/login', data: {
        'email': email,
        'password': password,
      });

      final token = response.data['token'];
      final respEmail = response.data['email'];
      final respPhone = response.data['phone_number'];

      if (token != null) {
        await _storage.write(key: 'jwt_token', value: token);
        if (respEmail != null) await _storage.write(key: 'session_email', value: respEmail.toString());
        if (respPhone != null) await _storage.write(key: 'session_phone', value: respPhone.toString());

        state = AuthState(
          isAuthenticated: true,
          email: respEmail?.toString(),
          phoneNumber: respPhone?.toString(),
        );
      }
    } on DioException catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: e.response?.data['detail'] ?? 'Invalid credentials credentials.',
      );
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

      final token = response.data['token'];
      final respEmail = response.data['email'];
      final respPhone = response.data['phone_number'];

      if (token != null) {
        await _storage.write(key: 'jwt_token', value: token);
        if (respEmail != null) await _storage.write(key: 'session_email', value: respEmail.toString());
        if (respPhone != null) await _storage.write(key: 'session_phone', value: respPhone.toString());

        state = AuthState(
          isAuthenticated: true,
          email: respEmail?.toString(),
          phoneNumber: respPhone?.toString(),
        );
      }
    } on DioException catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: e.response?.data['detail'] ?? 'Registration failed.',
      );
    }
  }

  Future<void> logout() async {
    await _storage.delete(key: 'jwt_token');
    await _storage.delete(key: 'session_email');
    await _storage.delete(key: 'session_phone');
    state = AuthState(isAuthenticated: false);
  }
}

final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  return AuthNotifier(ref.read(apiClientProvider));
});