import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/auth_provider.dart';
import '../theme.dart';
import 'register_screen.dart';

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final _emailController = TextEditingController();
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
            Text('Welcome Back', style: Theme.of(context).textTheme.headlineMedium),
            const SizedBox(height: 8),
            Text('Sign in to access your dashboard.', style: Theme.of(context).textTheme.bodyMedium),
            const SizedBox(height: 32),
            TextField(controller: _emailController, decoration: const InputDecoration(hintText: 'Email address')),
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
                ref.read(authProvider.notifier).login(
                  _emailController.text.trim(),
                  _passwordController.text.trim(),
                );
              },
              child: authState.isLoading
                  ? const SizedBox(height: 24, width: 24, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                  : const Text('Sign In'),
            ),
            const SizedBox(height: 16),
            Center(
              child: TextButton(
                onPressed: () {
                  Navigator.pushReplacement(context, MaterialPageRoute(builder: (context) => const RegisterScreen()));
                },
                child: const Text('Don\'t have an account? Register', style: TextStyle(color: AppTheme.primary, fontWeight: FontWeight.w600)),
              ),
            ),
          ],
        ),
      ),
    );
  }
}