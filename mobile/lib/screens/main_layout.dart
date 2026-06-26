import 'package:flutter/material.dart';
import 'home_screen.dart';
import 'settings_screen.dart';

class MainLayout extends StatefulWidget {
  const MainLayout({super.key});

  @override
  State<MainLayout> createState() => _MainLayoutState();
}

class _MainLayoutState extends State<MainLayout> {
  int _currentIndex = 0;

  final List<Widget> _screens = [
    const HomeScreen(),
    const SettingsScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(
        index: _currentIndex,
        children: _screens,
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
            BottomNavigationBarItem(icon: Icon(Icons.home_outlined), label: 'Home'),
            BottomNavigationBarItem(icon: Icon(Icons.tune), label: 'Settings'),
          ],
        ),
      ),
    );
  }
}