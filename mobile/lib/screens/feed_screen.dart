import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/alerts_provider.dart';
import '../models/incident_alert.dart';
import '../theme.dart';

class FeedScreen extends ConsumerWidget {
  final VoidCallback onNavigateToReport;

  const FeedScreen({super.key, required this.onNavigateToReport});

  Color _getTierColor(int tier) {
    switch (tier) {
      case 3: return AppTheme.error; // Critical Public Alert
      case 2: return AppTheme.primary; // Elevated Alert
      default: return const Color(0xFF8A8A8F); // Monitoring Tier 1
    }
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final alertsAsync = ref.watch(activeAlertsProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'SafeAlert Matrix',
          style: TextStyle(color: AppTheme.text, fontWeight: FontWeight.w600, fontSize: 20),
        ),
        backgroundColor: AppTheme.background,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, color: AppTheme.text, size: 20),
            onPressed: () => ref.invalidate(activeAlertsProvider),
          )
        ],
      ),
      body: alertsAsync.when(
        loading: () => const Center(child: CircularProgressIndicator(color: AppTheme.text, strokeWidth: 2)),
        error: (err, stack) => Padding(
          padding: const EdgeInsets.all(24.0),
          child: Center(
            child: Text(
              'Gateway Link Unstable. Pull down or check local ngrok connection state.',
              textAlign: TextAlign.center,
              style: TextStyle(color: AppTheme.error, fontSize: 14),
            ),
          ),
        ),
        data: (alerts) {
          if (alerts.isEmpty) {
            return RefreshIndicator(
              onRefresh: () async => ref.invalidate(activeAlertsProvider),
              color: AppTheme.text,
              child: ListView(
                physics: const AlwaysScrollableScrollPhysics(),
                children: [
                  SizedBox(height: MediaQuery.of(context).size.height * 0.25),
                  Padding(
                    padding: const EdgeInsets.all(32.0),
                    child: Column(
                      children: [
                        const Icon(Icons.shield_outlined, color: AppTheme.borders, size: 64),
                        const SizedBox(height: 16),
                        Text('Your Area is Secure', style: Theme.of(context).textTheme.headlineMedium?.copyWith(fontSize: 18)),
                        const SizedBox(height: 8),
                        Text(
                          'No critical localized anomalies are flagged across dispatch centers right now.',
                          textAlign: TextAlign.center,
                          style: Theme.of(context).textTheme.bodyMedium,
                        ),
                        const SizedBox(height: 24),
                        OutlinedButton(
                          onPressed: onNavigateToReport,
                          style: OutlinedButton.styleFrom(
                            side: const BorderSide(color: AppTheme.text),
                            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                          ),
                          child: const Text('Log Broadcast Form', style: TextStyle(color: AppTheme.text, fontWeight: FontWeight.w600)),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            );
          }

          return Scaffold(
            body: RefreshIndicator(
              onRefresh: () async => ref.invalidate(activeAlertsProvider),
              color: AppTheme.text,
              child: ListView.separated(
                padding: const EdgeInsets.all(24.0),
                itemCount: alerts.length,
                separatorBuilder: (context, index) => const SizedBox(height: 12),
                itemBuilder: (context, index) {
                  final alert = alerts[index];
                  return Container(
                    padding: const EdgeInsets.all(16.0),
                    decoration: BoxDecoration(
                      color: AppTheme.cards,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: AppTheme.borders),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              alert.incidentType,
                              style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 16, color: AppTheme.text),
                            ),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                              decoration: BoxDecoration(
                                color: _getTierColor(alert.tier).withOpacity(0.1),
                                borderRadius: BorderRadius.circular(6),
                              ),
                              child: Text(
                                'TIER ${alert.tier}',
                                style: TextStyle(
                                  color: _getTierColor(alert.tier),
                                  fontSize: 11,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                            )
                          ],
                        ),
                        const SizedBox(height: 8),
                        Row(
                          children: [
                            const Icon(Icons.location_on_outlined, size: 14, color: AppTheme.secondaryText),
                            const SizedBox(width: 4),
                            Expanded(
                              child: Text(
                                alert.location,
                                style: const TextStyle(color: AppTheme.secondaryText, fontSize: 13),
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 12),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              'Ref: ${alert.referenceCode}',
                              style: const TextStyle(fontFamily: 'Courier', fontSize: 12, color: AppTheme.secondaryText),
                            ),
                            Text(
                              'Confidence Score: ${alert.score}/100',
                              style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: AppTheme.text),
                            ),
                          ],
                        )
                      ],
                    ),
                  );
                },
              ),
            ),
            floatingActionButton: FloatingActionButton(
              onPressed: onNavigateToReport,
              backgroundColor: AppTheme.primary,
              elevation: 0,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              child: const Icon(Icons.add, color: Colors.white),
            ),
          );
        },
      ),
    );
  }
}