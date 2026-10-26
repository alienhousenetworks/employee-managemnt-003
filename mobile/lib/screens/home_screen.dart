import 'package:flutter/material.dart';
import '../services/api_client.dart';
import 'login_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key, required this.api, required this.organization});
  final ApiClient api;
  final Map<String, dynamic> organization;

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  List<dynamic> _posts = [];
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadFeed();
  }

  Future<void> _loadFeed() async {
    try {
      final posts = await widget.api.feed(widget.organization['id'].toString());
      if (mounted) {
        setState(() {
          _posts = posts;
          _error = null;
          _loading = false;
        });
      }
    } catch (error) {
      if (mounted) {
        setState(() {
          _error = error.toString().replaceFirst('Exception: ', '');
          _loading = false;
        });
      }
    }
  }

  Future<void> _signOut() async {
    await widget.api.signOut();
    if (!mounted) return;
    Navigator.of(context).pushAndRemoveUntil(
      MaterialPageRoute(builder: (_) => const LoginScreen()),
      (_) => false,
    );
  }

  @override
  Widget build(BuildContext context) {
    final items = <(IconData, String, String)>[
      (Icons.check_circle_outline, 'My work', 'Tasks and priorities.'),
      (Icons.dynamic_feed_outlined, 'Company feed', 'Team updates and announcements.'),
      (Icons.edit_note, 'EOD report', 'Evidence-linked daily report.'),
      (Icons.event_available_outlined, 'HR self-service', 'Attendance, leave and requests.'),
      (Icons.smart_toy_outlined, 'AI assistant', 'Recommendations and approved actions.'),
      (Icons.notifications_outlined, 'Notifications', 'Assignments and approvals.'),
    ];

    return Scaffold(
      appBar: AppBar(
        title: Text(widget.organization['name']?.toString() ?? 'ALIENHOUSE OS'),
        actions: [
          IconButton(onPressed: _signOut, icon: const Icon(Icons.logout), tooltip: 'Sign out'),
        ],
      ),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            const Text('Your agency workspace', style: TextStyle(fontSize: 26, fontWeight: FontWeight.w700)),
            const SizedBox(height: 6),
            const Text('People, projects and delivery in one place.'),
            const SizedBox(height: 18),
            if (_error != null)
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(color: const Color(0xFF351C24), borderRadius: BorderRadius.circular(12)),
                child: Text(_error!),
              ),
            const SizedBox(height: 8),
            const Text('Company feed', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700)),
            if (_loading)
              const Padding(padding: EdgeInsets.all(24), child: Center(child: CircularProgressIndicator()))
            else if (_posts.isEmpty)
              const Padding(padding: EdgeInsets.symmetric(vertical: 16), child: Text('No accessible posts were returned by the API.'))
            else
              ..._posts.map((post) {
                final p = post as Map<String, dynamic>;
                return Card(
                  color: const Color(0xFF121A26),
                  child: ListTile(
                    title: Text(p['author_name']?.toString() ?? 'Employee'),
                    subtitle: Padding(padding: const EdgeInsets.only(top: 8), child: Text(p['body']?.toString() ?? '')),
                    trailing: Text(p['post_type']?.toString() ?? 'UPDATE', style: const TextStyle(fontSize: 10)),
                  ),
                );
              }),
            const SizedBox(height: 16),
            const Text('Workspaces', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700)),
            ...items.map((item) => Card(
              color: const Color(0xFF121A26),
              child: ListTile(
                leading: Icon(item.$1),
                title: Text(item.$2),
                subtitle: Text(item.$3),
                trailing: const Icon(Icons.chevron_right),
                onTap: () => ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text('${item.$2} workflow is not yet connected.')),
                ),
              ),
            )),
          ],
        ),
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: 0,
        onDestinationSelected: (_) {},
        destinations: const [
          NavigationDestination(icon: Icon(Icons.home_outlined), label: 'Home'),
          NavigationDestination(icon: Icon(Icons.dynamic_feed_outlined), label: 'Feed'),
          NavigationDestination(icon: Icon(Icons.checklist_outlined), label: 'Work'),
          NavigationDestination(icon: Icon(Icons.chat_bubble_outline), label: 'Messages'),
        ],
      ),
    );
  }
}
