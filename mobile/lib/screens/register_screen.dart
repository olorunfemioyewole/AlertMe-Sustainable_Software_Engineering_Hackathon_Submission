import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/auth_provider.dart';
import '../theme.dart';
import 'login_screen.dart';

class RegisterScreen extends ConsumerStatefulWidget {
  const RegisterScreen({super.key});

  @override
  ConsumerState<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends ConsumerState<RegisterScreen> {
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
            Text('Create Account', style: Theme.of(context).textTheme.headlineMedium),
            const SizedBox(height: 8),
            Text('Join SafeAlert to broadcast security logs.', style: Theme.of(context).textTheme.bodyMedium),
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
              child: authState.isLoading
                  ? const SizedBox(height: 24, width: 24, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                  : const Text('Register & Sign Up'),
            ),
            const SizedBox(height: 16),
            Center(
              child: TextButton(
                onPressed: () {
                  Navigator.pushReplacement(context, MaterialPageRoute(builder: (context) => const LoginScreen()));
                },
                child: const Text('Already have an account? Sign In', style: TextStyle(color: AppTheme.primary, fontWeight: FontWeight.w600)),
              ),
            ),
          ],
        ),
      ),
    );
  }
}