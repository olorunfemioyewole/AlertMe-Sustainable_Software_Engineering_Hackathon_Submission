import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'theme.dart';
import 'providers/auth_provider.dart';
import 'screens/main_layout.dart';

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
      home: authState.isAuthenticated ? const MainLayout() : const AuthScreen(),
    );
  }
}

class AuthScreen extends ConsumerStatefulWidget {
  const AuthScreen({super.key});

  @override
  ConsumerState<AuthScreen> createState() => _AuthScreenState();
}

class _AuthScreenState extends ConsumerState<AuthScreen> {
  final _emailController = TextEditingController();
  final _phoneController = TextEditingController();
  final _passwordController = TextEditingController();

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authProvider);

    return Scaffold(
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('SafeAlert', style: Theme.of(context).textTheme.headlineMedium),
            const SizedBox(height: 8),
            Text('Secure community logging endpoint access.', style: Theme.of(context).textTheme.bodyMedium),
            const SizedBox(height: 32),
            TextField(controller: _emailController, decoration: const InputDecoration(hintText: 'Email address')),
            const SizedBox(height: 12),
            TextField(controller: _phoneController, decoration: const InputDecoration(hintText: 'Phone number (e.g. +234...)')),
            const SizedBox(height: 12),
            TextField(controller: _passwordController, obscureText: true, decoration: const InputDecoration(hintText: 'Password')),
            const SizedBox(height: 24),
            if (authState.errorMessage != null) ...[
              Text(authState.errorMessage!, style: const TextStyle(color: AppTheme.error)),
              const SizedBox(height: 12),
            ],
            ElevatedButton(
              onPressed: authState.isLoading
                  ? null
                  : () {
                ref.read(authProvider.notifier).register(
                  _emailController.text.trim(),
                  _phoneController.text.trim(),
                  _passwordController.text.trim(),
                );
              },
              child: authState.isLoading ? const CircularProgressIndicator(color: Colors.white) : const Text('Register & Sign In'),
            ),
          ],
        ),
      ),
    );
  }
}