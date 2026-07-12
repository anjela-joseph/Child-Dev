import 'package:flutter/material.dart';
import 'core/app_router.dart';

void main() {
  runApp(const ChildDevApp());
}

class ChildDevApp extends StatelessWidget {
  const ChildDevApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: 'Child Dev',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF5B7FFF)),
        useMaterial3: true,
      ),
      routerConfig: appRouter,
    );
  }
}
