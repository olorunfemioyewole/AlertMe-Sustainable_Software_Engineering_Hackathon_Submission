import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'theme.dart';
import 'providers/auth_provider.dart';
import 'screens/main_layout.dart';
import 'screens/login_screen.dart';

void main() {
  runApp(const ProviderScope(child: SafeAlertApp()));
}

class SafeAlertApp extends ConsumerWidget {
  const SafeAlertApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authProvider);

    return MaterialApp(
      title: 'SafeAlert',
      theme: AppTheme.lightTheme,
      debugShowCheckedModeBanner: false,
      home: authState.isAuthenticated ? const MainLayout() : const LoginScreen(),
    );
  }
}