import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final cards = [
      _FeatureCard(
        title: 'My Children',
        icon: Icons.child_care,
        subtitle: 'Manage your child profiles',
        route: '/children',
      ),
      _FeatureCard(
        title: 'Milestone Checklist',
        icon: Icons.checklist_rtl,
        subtitle: 'Review developmental milestones',
        route: '/milestones',
      ),
    ];

    return Scaffold(
      appBar: AppBar(title: const Text('Child Dev')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Welcome back', style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            Text('Start with one of the areas below.', style: Theme.of(context).textTheme.bodyLarge),
            const SizedBox(height: 16),
            Expanded(
              child: GridView.builder(
                itemCount: cards.length,
                gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(crossAxisCount: 2, mainAxisSpacing: 12, crossAxisSpacing: 12),
                itemBuilder: (context, index) {
                  final card = cards[index];
                  return InkWell(
                    onTap: () => context.go(card.route),
                    child: Card(
                      child: Padding(
                        padding: const EdgeInsets.all(16),
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(card.icon, size: 36, color: const Color(0xFF5B7FFF)),
                            const SizedBox(height: 8),
                            Text(card.title, textAlign: TextAlign.center, style: const TextStyle(fontWeight: FontWeight.bold)),
                            const SizedBox(height: 4),
                            Text(card.subtitle, textAlign: TextAlign.center, style: Theme.of(context).textTheme.bodySmall),
                          ],
                        ),
                      ),
                    ),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _FeatureCard {
  const _FeatureCard({required this.title, required this.icon, required this.subtitle, required this.route});

  final String title;
  final IconData icon;
  final String subtitle;
  final String route;
}
