import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/auth_provider.dart';
import '../theme.dart';

class SettingsScreen extends ConsumerWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Read the active state to handle loading indicators during session changes
    final authState = ref.watch(authProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'System Configurations',
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
              Text(
                'Active Session Profile',
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
                      'Routing Account Identifier',
                      style: TextStyle(color: AppTheme.secondaryText, fontSize: 12),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'test@example.com', // Explicit session tracking parameter
                      style: const TextStyle(color: AppTheme.text, fontSize: 15, fontWeight: FontWeight.w500),
                    ),
                    const SizedBox(height: 16),
                    const Text(
                      'Gateway Environment',
                      style: TextStyle(color: AppTheme.secondaryText, fontSize: 12),
                    ),
                    const SizedBox(height: 4),
                    const Text(
                      'Mobile API Port Gateway (8001)',
                      style: TextStyle(color: AppTheme.text, fontSize: 15, fontWeight: FontWeight.w500),
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
                child: const Text('Evacuate Session Keys'),
              ),
              const SizedBox(height: 12),
              const Center(
                child: Text(
                  'SafeAlert v1.0.0 Stable Build',
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