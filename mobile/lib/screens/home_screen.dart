import 'package:flutter/material.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});
  @override
  Widget build(BuildContext context) {
    final items = <(IconData, String, String)>[
      (Icons.check_circle_outline, 'My work', 'Tasks and priorities will appear when signed in.'),
      (Icons.dynamic_feed_outlined, 'Company feed', 'Updates, comments and team announcements.'),
      (Icons.edit_note, 'EOD report', 'Prepare a report linked to verified work records.'),
      (Icons.event_available_outlined, 'HR self-service', 'Attendance, leave and employee requests.'),
      (Icons.smart_toy_outlined, 'AI assistant', 'Recommendations and approval-gated actions.'),
      (Icons.notifications_outlined, 'Notifications', 'Assignments, mentions and approval requests.'),
    ];
    return Scaffold(
      appBar: AppBar(title: const Text('ALIENHOUSE OS'), actions: [IconButton(onPressed: () {}, icon: const Icon(Icons.account_circle_outlined), tooltip: 'Profile')]),
      body: SafeArea(child: ListView(padding: const EdgeInsets.all(16), children: [
        const Text('Your agency workspace', style: TextStyle(fontSize: 26, fontWeight: FontWeight.w700)),
        const SizedBox(height: 6),
        Text('People, projects and delivery — in one place.', style: TextStyle(color: Theme.of(context).colorScheme.onSurfaceVariant)),
        const SizedBox(height: 20),
        Container(padding: const EdgeInsets.all(14), decoration: BoxDecoration(color: const Color(0xFF1B281A), borderRadius: BorderRadius.circular(14), border: Border.all(color: const Color(0xFF3D4D34))), child: const Text('Offline preview. Sign-in and API configuration are required to load live data. No metrics are being inferred.')),
        const SizedBox(height: 12),
        ...items.map((item) => Card(color: const Color(0xFF121A26), child: ListTile(leading: Icon(item.$1), title: Text(item.$2), subtitle: Text(item.$3), trailing: const Icon(Icons.chevron_right), onTap: () => ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('${item.$2} will open after the authenticated workflow is connected.')))))),
      ])),
      bottomNavigationBar: NavigationBar(selectedIndex: 0, onDestinationSelected: (_) {}, destinations: const [NavigationDestination(icon: Icon(Icons.home_outlined), label: 'Home'), NavigationDestination(icon: Icon(Icons.dynamic_feed_outlined), label: 'Feed'), NavigationDestination(icon: Icon(Icons.checklist_outlined), label: 'Work'), NavigationDestination(icon: Icon(Icons.chat_bubble_outline), label: 'Messages')]),
    );
  }
}
