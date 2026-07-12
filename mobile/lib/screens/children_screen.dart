import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../core/api_client.dart';

class ChildrenScreen extends StatefulWidget {
  const ChildrenScreen({super.key});

  @override
  State<ChildrenScreen> createState() => _ChildrenScreenState();
}

class _ChildrenScreenState extends State<ChildrenScreen> {
  bool _loading = true;
  final List<Map<String, dynamic>> _children = [];
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadChildren();
  }

  Future<void> _loadChildren() async {
    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final data = await ApiClient.instance.fetchChildren();
      if (!mounted) return;
      setState(() {
        _children.clear();
        _children.addAll(data);
      });
    } catch (error) {
      if (!mounted) return;
      setState(() => _error = ApiClient.instance.getErrorMessage(error));
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _addChild() async {
    final nameController = TextEditingController();
    final dobController = TextEditingController();
    final notesController = TextEditingController();
    String gender = 'M';

    final result = await showDialog<Map<String, dynamic>>(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('Add child'),
          content: StatefulBuilder(
            builder: (context, setState) {
              return Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  TextField(controller: nameController, decoration: const InputDecoration(labelText: 'Name')),
                  const SizedBox(height: 8),
                  TextField(controller: dobController, decoration: const InputDecoration(labelText: 'Date of birth (YYYY-MM-DD)')),
                  const SizedBox(height: 8),
                  DropdownButtonFormField<String>(
                    initialValue: gender,
                    items: const [DropdownMenuItem(value: 'M', child: Text('Male')), DropdownMenuItem(value: 'F', child: Text('Female'))],
                    onChanged: (value) => setState(() => gender = value ?? 'M'),
                    decoration: const InputDecoration(labelText: 'Gender'),
                  ),
                  const SizedBox(height: 8),
                  TextField(controller: notesController, decoration: const InputDecoration(labelText: 'Notes')),
                ],
              );
            },
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
            FilledButton(
              onPressed: () => Navigator.pop(context, {
                'name': nameController.text.trim(),
                'date_of_birth': dobController.text.trim(),
                'gender': gender,
                'notes': notesController.text.trim(),
              }),
              child: const Text('Save'),
            ),
          ],
        );
      },
    );

    if (result == null) return;

    try {
      await ApiClient.instance.createChild(
        name: result['name']!,
        dateOfBirth: result['date_of_birth']!,
        gender: result['gender']!,
        notes: result['notes']!,
      );
      await _loadChildren();
    } catch (error) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(ApiClient.instance.getErrorMessage(error))));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Children')),
      floatingActionButton: FloatingActionButton(onPressed: _addChild, child: const Icon(Icons.add)),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(child: Text(_error!))
              : _children.isEmpty
                  ? const Center(child: Text('No children yet. Add one to get started.'))
                  : ListView.builder(
                      itemCount: _children.length,
                      itemBuilder: (context, index) {
                        final child = _children[index];
                        final age = child['age_in_years'] as int? ?? 0;
                        final ageDisplay = age < 3
                            ? 'Under 3 years'
                            : age > 7
                                ? 'Over 7 years'
                                : '$age years old';
                        return ListTile(
                          leading: const CircleAvatar(child: Icon(Icons.face)),
                          title: Text(child['name'] ?? ''),
                          subtitle: Text('$ageDisplay • ${child['gender'] ?? ''}'),
                          trailing: const Icon(Icons.chevron_right),
                          onTap: (age >= 3 && age <= 7)
                              ? () => context.push('/assessment', extra: {
                                    'childId': child['id'] as int,
                                    'childName': child['name'] as String,
                                    'childAge': age,
                                  })
                              : () => ScaffoldMessenger.of(context).showSnackBar(
                                    const SnackBar(content: Text('Assessments are available for children aged 3–7.')),
                                  ),
                        );
                      },
                    ),
    );
  }
}
