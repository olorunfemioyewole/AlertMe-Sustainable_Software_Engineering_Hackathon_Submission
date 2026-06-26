import 'package:flutter/material.dart';
import 'feed_screen.dart';
import 'report_screen.dart';
import 'settings_screen.dart'; // Import Phase 4 Screen

class MainLayout extends StatefulWidget {
  const MainLayout({super.key});

  @override
  State<MainLayout> createState() => _MainLayoutState();
}

class _MainLayoutState extends State<MainLayout> {
  int _currentIndex = 0;

  @override
  Widget build(BuildContext context) {
    final List<Widget> screens = [
      FeedScreen(onNavigateToReport: () => setState(() => _currentIndex = 1)),
      const ReportScreen(),
      const SettingsScreen(), // Replaced the final mock view with our live settings component
    ];

    return Scaffold(
      body: IndexedStack(
        index: _currentIndex,
        children: screens,
      ),
      bottomNavigationBar: Container(
        decoration: const BoxDecoration(
          border: Border(top: BorderSide(color: Color(0xFFECECEC), width: 1)),
        ),
        child: BottomNavigationBar(
          currentIndex: _currentIndex,
          backgroundColor: Colors.white,
          selectedItemColor: const Color(0xFFF18F01),
          unselectedItemColor: const Color(0xFF666666),
          elevation: 0,
          type: BottomNavigationBarType.fixed,
          onTap: (index) => setState(() => _currentIndex = index),
          items: const [
            BottomNavigationBarItem(icon: Icon(Icons.shield_outlined), label: 'Feed'),
            BottomNavigationBarItem(icon: Icon(Icons.add_circle_outline), label: 'Report'),
            BottomNavigationBarItem(icon: Icon(Icons.tune), label: 'Settings'),
          ],
        ),
      ),
    );
  }
}