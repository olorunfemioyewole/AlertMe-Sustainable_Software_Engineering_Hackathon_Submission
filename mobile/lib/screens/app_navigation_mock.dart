import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/auth_provider.dart';

class MockHomeScreen extends StatelessWidget {
  const MockHomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('SafeAlert Feed', style: TextStyle(color: Color(0xFF111111), fontWeight: FontWeight.bold)),
        backgroundColor: Colors.white,
        elevation: 0,
      ),
      body: const Center(child: Text('No active local alerts recorded.')),
    );
  }
}

class MockSettingsScreen extends ConsumerWidget {
  const MockSettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      body: Center(
        child: TextButton(
          onPressed: () => ref.read(authProvider.notifier).logout(),
          child: const Text('Logout', style: TextStyle(color: Colors.red, fontWeight: FontWeight.w600)),
        ),
      ),
    );
  }
}