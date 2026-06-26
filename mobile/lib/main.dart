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
    // ref.watch forces this build method to re-run the instant the auth state updates!
    final authState = ref.watch(authProvider);

    return MaterialApp(
      title: 'Alert Me',
      theme: AppTheme.lightTheme,
      debugShowCheckedModeBanner: false,
      // The switch happens immediately in memory now without requiring a manual refresh
      home: authState.isAuthenticated
          ? const MainLayout()
          : const LoginScreen(),
    );
  }
}