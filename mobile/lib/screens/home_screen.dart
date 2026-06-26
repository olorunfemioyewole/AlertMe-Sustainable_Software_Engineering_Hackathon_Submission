import 'package:flutter/material.dart';
import '../theme.dart';
import 'report_screen.dart';

// Simple global tracking provider for hackathon mock persistence of submitted reports
import 'package:flutter_riverpod/flutter_riverpod.dart';
final userSubmittedReportsProvider = StateProvider<List<Map<String, dynamic>>>((ref) => []);

class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final reports = ref.watch(userSubmittedReportsProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('My Reports', style: TextStyle(color: AppTheme.text, fontWeight: FontWeight.w600, fontSize: 20)),
        backgroundColor: AppTheme.background,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.notifications_none, color: AppTheme.text),
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('No new system broadcast notifications.')),
              );
            },
          )
        ],
      ),
      body: reports.isEmpty
          ? Center(
        child: Padding(
          padding: const EdgeInsets.all(32.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.assignment_outlined, color: AppTheme.borders, size: 64),
              const SizedBox(height: 16),
              Text('No Reports Logged', style: Theme.of(context).textTheme.headlineMedium?.copyWith(fontSize: 18)),
              const SizedBox(height: 8),
              Text('You haven\'t broadcasted any localized incident alerts yet.', textAlign: TextAlign.center, style: Theme.of(context).textTheme.bodyMedium),
              const SizedBox(height: 24),
              OutlinedButton(
                onPressed: () {
                  Navigator.push(context, MaterialPageRoute(builder: (context) => const ReportScreen()));
                },
                style: OutlinedButton.styleFrom(
                  side: const BorderSide(color: AppTheme.text),
                  padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
                child: const Text('File Security Report', style: TextStyle(color: AppTheme.text, fontWeight: FontWeight.w600)),
              ),
            ],
          ),
        ),
      )
          : ListView.separated(
        padding: const EdgeInsets.all(24.0),
        itemCount: reports.length,
        separatorBuilder: (context, index) => const SizedBox(height: 12),
        itemBuilder: (context, index) {
          final report = reports[index];
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
                    Text(report['type'], style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 16, color: AppTheme.text)),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(color: AppTheme.primary.withOpacity(0.1), borderRadius: BorderRadius.circular(6)),
                      child: Text(report['status'].toUpperCase(), style: const TextStyle(color: AppTheme.primary, fontSize: 11, fontWeight: FontWeight.w600)),
                    )
                  ],
                ),
                const SizedBox(height: 8),
                Text(report['location'], style: const TextStyle(color: AppTheme.secondaryText, fontSize: 13)),
                const SizedBox(height: 12),
                Text('Ref Code: ${report['ref']}', style: const TextStyle(fontFamily: 'Courier', fontSize: 12, color: AppTheme.secondaryText)),
              ],
            ),
          );
        },
      ),
      floatingActionButton: reports.isNotEmpty
          ? FloatingActionButton(
        onPressed: () {
          Navigator.push(context, MaterialPageRoute(builder: (context) => const ReportScreen()));
        },
        backgroundColor: AppTheme.primary,
        elevation: 0,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        child: const Icon(Icons.add, color: Colors.white),
      )
          : null,
    );
  }
}