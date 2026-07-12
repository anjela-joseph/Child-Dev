import 'package:flutter/material.dart';
import '../core/api_client.dart';

class MilestoneChecklistScreen extends StatefulWidget {
  const MilestoneChecklistScreen({super.key});

  @override
  State<MilestoneChecklistScreen> createState() => _MilestoneChecklistScreenState();
}

class _MilestoneChecklistScreenState extends State<MilestoneChecklistScreen> {
  int _age = 5;
  bool _loading = true;
  Map<String, dynamic>? _data;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadChecklist();
  }

  Future<void> _loadChecklist() async {
    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final data = await ApiClient.instance.fetchChecklist(_age);
      if (!mounted) return;
      setState(() => _data = data);
    } catch (error) {
      if (!mounted) return;
      setState(() => _error = ApiClient.instance.getErrorMessage(error));
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Milestones')),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                const Text('Age:'),
                const SizedBox(width: 12),
                DropdownButton<int>(
                  value: _age,
                  items: List.generate(5, (index) => 3 + index)
                      .map((age) => DropdownMenuItem(value: age, child: Text('$age')))
                      .toList(),
                  onChanged: (value) {
                    if (value == null) return;
                    setState(() => _age = value);
                    _loadChecklist();
                  },
                ),
              ],
            ),
          ),
          Expanded(
            child: _loading
                ? const Center(child: CircularProgressIndicator())
                : _error != null
                    ? Center(child: Text(_error!))
                    : _data == null
                        ? const Center(child: Text('No checklist data'))
                        : ListView(
                            children: [
                              if (_data!['milestone_domains'] != null)
                                ...(_data!['milestone_domains'] as List).map((domain) {
                                  final items = domain['items'] as List;
                                  return Card(
                                    margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                                    child: ExpansionTile(
                                      title: Text(domain['domain_label'] ?? domain['domain'] ?? 'Domain'),
                                      children: items.map<Widget>((item) {
                                        return ListTile(
                                          title: Text(item['description'] ?? ''),
                                          subtitle: Text('Severity: ${item['severity_if_missed'] ?? '-'}'),
                                        );
                                      }).toList(),
                                    ),
                                  );
                                }),
                            ],
                          ),
          ),
        ],
      ),
    );
  }
}
