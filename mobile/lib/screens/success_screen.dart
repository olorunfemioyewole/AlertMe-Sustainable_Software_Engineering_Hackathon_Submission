import 'package:flutter/material.dart';
import '../theme.dart';

class SuccessScreen extends StatelessWidget {
  final String referenceCode;

  const SuccessScreen({super.key, required this.referenceCode});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            const Icon(Icons.check_circle_outline, color: AppTheme.primary, size: 80),
            const SizedBox(height: 24),
            Text('Report Dispatched', style: Theme.of(context).textTheme.headlineMedium),
            const SizedBox(height: 12),
            Text(
              'Your submission is live on the community feed matrix. Central sorting engine tracking token allocated below:',
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodyMedium,
            ),
            const SizedBox(height: 24),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
              decoration: BoxDecoration(
                color: AppTheme.cards,
                border: Border.all(color: AppTheme.borders),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Text(
                referenceCode,
                style: const TextStyle(
                  fontSize: 28,
                  fontWeight: FontWeight.w600,
                  letterSpacing: 2,
                  color: AppTheme.text,
                ),
              ),
            ),
            const SizedBox(height: 48),
            ElevatedButton(
              onPressed: () {
                // Return smoothly back to primary tab structure layers
                Navigator.of(context).popUntil((route) => route.isFirst);
              },
              style: ElevatedButton.styleFrom(backgroundColor: AppTheme.text),
              child: const Text('Back to Dashboard', style: TextStyle(color: Colors.white)),
            ),
          ],
        ),
      ),
    );
  }
}