import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/auth_provider.dart';
import '../theme.dart';

class SettingsScreen extends ConsumerWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authProvider);

    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: const Text(
          'Settings',
          style: TextStyle(color: AppTheme.text, fontWeight: FontWeight.w600, fontSize: 20),
        ),
        backgroundColor: AppTheme.background,
        elevation: 0,
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Your Account',
                style: TextStyle(
                    color: AppTheme.text,
                    fontWeight: FontWeight.w600,
                    fontSize: 14,
                    letterSpacing: -0.2
                ),
              ),
              const SizedBox(height: 12),
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: AppTheme.cards,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: AppTheme.borders),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Email',
                      style: TextStyle(color: AppTheme.secondaryText, fontSize: 12),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      authState.email ?? 'Not Available',
                      style: const TextStyle(color: AppTheme.text, fontSize: 15, fontWeight: FontWeight.w500),
                    ),
                    const SizedBox(height: 16),
                    const Text(
                      'Phone number',
                      style: TextStyle(color: AppTheme.secondaryText, fontSize: 12),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      authState.phoneNumber ?? 'Not Available',
                      style: const TextStyle(color: AppTheme.text, fontSize: 15, fontWeight: FontWeight.w500),
                    ),
                  ],
                ),
              ),
              const Spacer(),
              if (authState.isLoading) ...[
                const Center(child: CircularProgressIndicator(color: AppTheme.text, strokeWidth: 2)),
                const SizedBox(height: 16),
              ],
              ElevatedButton(
                onPressed: authState.isLoading
                    ? null
                    : () => ref.read(authProvider.notifier).logout(),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFFFAFAFA),
                  foregroundColor: AppTheme.error,
                  side: const BorderSide(color: AppTheme.borders),
                ),
                child: const Text('Sign Out'),
              ),
              const SizedBox(height: 12),
              const Center(
                child: Text(
                  'Alert Me v1.0.0',
                  style: TextStyle(color: AppTheme.secondaryText, fontSize: 12),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}