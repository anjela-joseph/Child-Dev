import 'package:flutter/material.dart';
import '../core/api_client.dart';

class AssessmentScreen extends StatefulWidget {
  final int childId;
  final String childName;
  final int childAge;

  const AssessmentScreen({
    super.key,
    required this.childId,
    required this.childName,
    required this.childAge,
  });

  @override
  State<AssessmentScreen> createState() => _AssessmentScreenState();
}

class _AssessmentScreenState extends State<AssessmentScreen> {
  bool _loading = true;
  bool _submitting = false;
  String? _error;
  Map<String, dynamic>? _checklist;
  int? _assessmentId;

  final Map<int, String> _milestoneResponses = {};
  final Map<int, bool> _redFlagResponses = {};

  List<Map<String, dynamic>> get _allDomains =>
      (_checklist?['milestone_domains'] as List?)
          ?.cast<Map<String, dynamic>>() ??
          [];

  List<Map<String, dynamic>> get _allRedFlags =>
      (_checklist?['red_flags'] as List?)
          ?.cast<Map<String, dynamic>>() ??
          [];

  int get _totalMilestones =>
      _allDomains.fold(0, (sum, d) => sum + (d['items'] as List).length);

  @override
  void initState() {
    super.initState();
    _setup();
  }

  Future<void> _setup() async {
    try {
      final assessment = await ApiClient.instance.createAssessment(
        childId: widget.childId,
      );
      final checklist = await ApiClient.instance.fetchChecklist(widget.childAge);
      if (!mounted) return;
      setState(() {
        _assessmentId = assessment['id'] as int;
        _checklist = checklist;
      });
    } catch (error) {
      if (!mounted) return;
      setState(() => _error = ApiClient.instance.getErrorMessage(error));
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _submit() async {
    if (_assessmentId == null) return;
    if (_milestoneResponses.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please answer at least one milestone before submitting.')),
      );
      return;
    }

    setState(() => _submitting = true);
    try {
      final milestoneResponses = _milestoneResponses.entries
          .map((e) => {
                'milestone_item': e.key,
                'response': e.value,
                'parent_note': '',
              })
          .toList();

      final redFlagResponses = _redFlagResponses.entries
          .map((e) => {'red_flag': e.key, 'is_present': e.value})
          .toList();

      final result = await ApiClient.instance.submitAssessment(
        assessmentId: _assessmentId!,
        milestoneResponses: milestoneResponses,
        redFlagResponses: redFlagResponses,
      );

      if (!mounted) return;
      Navigator.of(context).pushReplacement(MaterialPageRoute(
        builder: (_) => ResultsScreen(
          result: result,
          assessmentId: _assessmentId!,
        ),
      ));
    } catch (error) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(ApiClient.instance.getErrorMessage(error))),
      );
    } finally {
      if (mounted) setState(() => _submitting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF5F7FF),
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Assessment — ${widget.childName}',
                style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            Text('Age ${widget.childAge} · ${_milestoneResponses.length}/$_totalMilestones answered',
                style: const TextStyle(fontSize: 12, fontWeight: FontWeight.normal)),
          ],
        ),
        actions: [
          if (!_loading && _error == null)
            _submitting
                ? const Padding(
                    padding: EdgeInsets.all(16),
                    child: SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    ),
                  )
                : FilledButton.icon(
                    onPressed: _submit,
                    icon: const Icon(Icons.send, size: 16),
                    label: const Text('Submit'),
                    style: FilledButton.styleFrom(
                      backgroundColor: Colors.green,
                      foregroundColor: Colors.white,
                    ),
                  ),
          const SizedBox(width: 8),
        ],
      ),
      body: _loading
          ? const Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  CircularProgressIndicator(),
                  SizedBox(height: 16),
                  Text('Loading questionnaire...', style: TextStyle(color: Colors.grey)),
                ],
              ),
            )
          : _error != null
              ? Center(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(Icons.error_outline, size: 48, color: Colors.red),
                      const SizedBox(height: 12),
                      Text(_error!, style: const TextStyle(color: Colors.red)),
                      const SizedBox(height: 12),
                      FilledButton(onPressed: _setup, child: const Text('Retry')),
                    ],
                  ),
                )
              : _buildQuestionnaire(),
    );
  }

  Widget _buildQuestionnaire() {
    // Progress bar
    final progress = _totalMilestones == 0
        ? 0.0
        : _milestoneResponses.length / _totalMilestones;

    return Column(
      children: [
        // Progress bar
        LinearProgressIndicator(
          value: progress,
          backgroundColor: Colors.grey[200],
          color: Colors.green,
          minHeight: 6,
        ),

        Expanded(
          child: ListView(
            padding: const EdgeInsets.all(16),
            children: [
              // ── Milestone domains ──
              ..._allDomains.map((domain) => _DomainSection(
                    domain: domain,
                    responses: _milestoneResponses,
                    onResponse: (itemId, response) {
                      setState(() => _milestoneResponses[itemId] = response);
                    },
                  )),

              // ── Red flags ──
              if (_allRedFlags.isNotEmpty) ...[
                const SizedBox(height: 8),
                _SectionHeader(
                  icon: Icons.flag_rounded,
                  iconColor: Colors.red,
                  title: 'Red Flag Questions',
                  subtitle: 'Answer honestly — helps provide better guidance.',
                ),
                const SizedBox(height: 8),
                ..._allRedFlags.map((rf) => _RedFlagCard(
                      redFlag: rf,
                      current: _redFlagResponses[rf['id'] as int],
                      onChanged: (val) {
                        setState(() => _redFlagResponses[rf['id'] as int] = val);
                      },
                    )),
              ],

              const SizedBox(height: 24),

              // ── Submit button ──
              FilledButton.icon(
                onPressed: _submitting ? null : _submit,
                icon: _submitting
                    ? const SizedBox(
                        width: 16,
                        height: 16,
                        child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                      )
                    : const Icon(Icons.check_circle_outline),
                label: Text(_submitting ? 'Submitting...' : 'Submit Assessment'),
                style: FilledButton.styleFrom(
                  minimumSize: const Size.fromHeight(50),
                  backgroundColor: Colors.green,
                ),
              ),
              const SizedBox(height: 8),
              const Text(
                'All milestone responses will be scored automatically.',
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 12, color: Colors.grey),
              ),
              const SizedBox(height: 40),
            ],
          ),
        ),
      ],
    );
  }
}

// ── Domain section ────────────────────────────────────────────

class _DomainSection extends StatelessWidget {
  final Map<String, dynamic> domain;
  final Map<int, String> responses;
  final void Function(int itemId, String response) onResponse;

  const _DomainSection({
    required this.domain,
    required this.responses,
    required this.onResponse,
  });

  @override
  Widget build(BuildContext context) {
    final items = (domain['items'] as List).cast<Map<String, dynamic>>();
    final label = domain['domain_label'] as String? ?? domain['domain'] as String? ?? '';
    final answered = items.where((i) => responses.containsKey(i['id'] as int)).length;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _SectionHeader(
          icon: Icons.checklist_rounded,
          iconColor: const Color(0xFF5B7FFF),
          title: label,
          subtitle: '$answered of ${items.length} answered',
        ),
        const SizedBox(height: 8),
        ...items.map((item) => _MilestoneCard(
              item: item,
              selected: responses[item['id'] as int],
              onSelect: (r) => onResponse(item['id'] as int, r),
            )),
        const SizedBox(height: 8),
      ],
    );
  }
}

// ── Milestone card ────────────────────────────────────────────

class _MilestoneCard extends StatelessWidget {
  final Map<String, dynamic> item;
  final String? selected;
  final void Function(String) onSelect;

  const _MilestoneCard({
    required this.item,
    required this.selected,
    required this.onSelect,
  });

  static const _options = [
    ('met', 'Met', Colors.green, '✅'),
    ('emerging', 'Emerging', Colors.blue, '🔵'),
    ('not_yet', 'Not Yet', Colors.orange, '🟡'),
    ('concerned', 'Concerned', Colors.red, '🔴'),
  ];

  @override
  Widget build(BuildContext context) {
    final severity = item['severity_if_missed'] as String? ?? '';
    final isHighSeverity = severity == 'high';

    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      elevation: selected != null ? 0 : 1,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(10),
        side: BorderSide(
          color: selected != null
              ? _colorForResponse(selected!)
              : (isHighSeverity ? Colors.red.shade200 : Colors.transparent),
          width: 1.5,
        ),
      ),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    item['description'] as String? ?? '',
                    style: const TextStyle(fontSize: 14, height: 1.4),
                  ),
                ),
                if (isHighSeverity)
                  const Padding(
                    padding: EdgeInsets.only(left: 8),
                    child: Tooltip(
                      message: 'High severity if missed',
                      child: Icon(Icons.warning_amber_rounded, color: Colors.red, size: 18),
                    ),
                  ),
              ],
            ),
            const SizedBox(height: 10),
            // Response buttons
            Wrap(
              spacing: 6,
              runSpacing: 6,
              children: _options.map((opt) {
                final (value, label, color, emoji) = opt;
                final isSelected = selected == value;
                return GestureDetector(
                  onTap: () => onSelect(value),
                  child: AnimatedContainer(
                    duration: const Duration(milliseconds: 150),
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 7),
                    decoration: BoxDecoration(
                      color: isSelected ? color.withOpacity(0.15) : Colors.grey[100],
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(
                        color: isSelected ? color : Colors.grey.shade300,
                        width: isSelected ? 1.5 : 1,
                      ),
                    ),
                    child: Text(
                      '$emoji $label',
                      style: TextStyle(
                        fontSize: 12,
                        fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                        color: isSelected ? color : Colors.grey[600],
                      ),
                    ),
                  ),
                );
              }).toList(),
            ),
          ],
        ),
      ),
    );
  }

  Color _colorForResponse(String r) {
    switch (r) {
      case 'met':       return Colors.green;
      case 'emerging':  return Colors.blue;
      case 'not_yet':   return Colors.orange;
      case 'concerned': return Colors.red;
      default:          return Colors.grey;
    }
  }
}

// ── Red flag card ─────────────────────────────────────────────

class _RedFlagCard extends StatelessWidget {
  final Map<String, dynamic> redFlag;
  final bool? current;
  final void Function(bool) onChanged;

  const _RedFlagCard({
    required this.redFlag,
    required this.current,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      color: Colors.red[50],
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(10),
        side: BorderSide(
          color: current == true ? Colors.red.shade300 : Colors.red.shade100,
        ),
      ),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              redFlag['description'] as String? ?? '',
              style: const TextStyle(fontSize: 14, height: 1.4),
            ),
            const SizedBox(height: 10),
            Row(
              children: [
                _FlagButton(
                  label: '⚠️ Yes, I notice this',
                  selected: current == true,
                  selectedColor: Colors.red,
                  onTap: () => onChanged(true),
                ),
                const SizedBox(width: 8),
                _FlagButton(
                  label: '✅ Not present',
                  selected: current == false,
                  selectedColor: Colors.green,
                  onTap: () => onChanged(false),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _FlagButton extends StatelessWidget {
  final String label;
  final bool selected;
  final Color selectedColor;
  final VoidCallback onTap;

  const _FlagButton({
    required this.label,
    required this.selected,
    required this.selectedColor,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 150),
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 7),
        decoration: BoxDecoration(
          color: selected ? selectedColor.withOpacity(0.12) : Colors.white,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: selected ? selectedColor : Colors.grey.shade300,
            width: selected ? 1.5 : 1,
          ),
        ),
        child: Text(
          label,
          style: TextStyle(
            fontSize: 12,
            fontWeight: selected ? FontWeight.bold : FontWeight.normal,
            color: selected ? selectedColor : Colors.grey[600],
          ),
        ),
      ),
    );
  }
}

// ── Section header ────────────────────────────────────────────

class _SectionHeader extends StatelessWidget {
  final IconData icon;
  final Color iconColor;
  final String title;
  final String subtitle;

  const _SectionHeader({
    required this.icon,
    required this.iconColor,
    required this.title,
    required this.subtitle,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: iconColor.withOpacity(0.1),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Icon(icon, color: iconColor, size: 20),
        ),
        const SizedBox(width: 12),
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title,
                style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
            Text(subtitle,
                style: const TextStyle(fontSize: 12, color: Colors.grey)),
          ],
        ),
      ],
    );
  }
}

// ── Results Screen ────────────────────────────────────────────

class ResultsScreen extends StatefulWidget {
  final Map<String, dynamic> result;
  final int assessmentId;

  const ResultsScreen({
    super.key,
    required this.result,
    required this.assessmentId,
  });

  @override
  State<ResultsScreen> createState() => _ResultsScreenState();
}

class _ResultsScreenState extends State<ResultsScreen> {
  List<Map<String, dynamic>> _referrals = [];
  bool _loadingReferrals = true;
  bool _acknowledged = false;

  @override
  void initState() {
    super.initState();
    _loadReferrals();
  }

  Future<void> _loadReferrals() async {
    try {
      final data = await ApiClient.instance.fetchReferrals(widget.assessmentId);
      if (!mounted) return;
      setState(() => _referrals = data);
    } catch (_) {
    } finally {
      if (mounted) setState(() => _loadingReferrals = false);
    }
  }

  Future<void> _acknowledge(int referralId) async {
    try {
      await ApiClient.instance.acknowledgeReferral(referralId);
      if (!mounted) return;
      setState(() => _acknowledged = true);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Acknowledged — thank you!')),
      );
    } catch (_) {}
  }

  Color _levelColor(String level) {
    switch (level) {
      case 'green':  return Colors.green;
      case 'yellow': return const Color(0xFFD4A800);
      case 'orange': return Colors.orange;
      case 'red':    return Colors.red;
      default:       return Colors.grey;
    }
  }

  String _levelLabel(String level) {
    switch (level) {
      case 'green':  return '🟢  On Track';
      case 'yellow': return '🟡  Monitor Closely';
      case 'orange': return '🟠  Suggest Screening';
      case 'red':    return '🔴  Seek Evaluation';
      default:       return level;
    }
  }

  @override
  Widget build(BuildContext context) {
    final level = widget.result['risk_level'] as String? ?? 'green';
    final flags = (widget.result['flags'] as Map?)?.cast<String, dynamic>() ?? {};
    final domains = (widget.result['domains_with_concerns'] as List?)?.cast<String>() ?? [];
    final summary = widget.result['summary_message'] as String? ?? '';
    final color = _levelColor(level);

    return Scaffold(
      backgroundColor: const Color(0xFFF5F7FF),
      appBar: AppBar(title: const Text('Assessment Results')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Risk level
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              borderRadius: BorderRadius.circular(14),
              border: Border.all(color: color, width: 2),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(_levelLabel(level),
                    style: TextStyle(
                        fontSize: 22, fontWeight: FontWeight.bold, color: color)),
                const SizedBox(height: 10),
                Text(summary,
                    style: const TextStyle(fontSize: 14, height: 1.6, color: Colors.black87)),
              ],
            ),
          ),
          const SizedBox(height: 16),

          // Pattern flags
          if (flags.values.any((v) => v == true)) ...[
            const Text('Pattern Indicators',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 6,
              children: flags.entries.map((e) {
                final active = e.value == true;
                return Chip(
                  avatar: Icon(
                    active ? Icons.warning_amber_rounded : Icons.check_circle_outline,
                    size: 16,
                    color: active ? Colors.red[700] : Colors.grey,
                  ),
                  label: Text(
                    e.key.replaceAll('_', ' ').toUpperCase(),
                    style: TextStyle(
                        fontSize: 11,
                        color: active ? Colors.red[800] : Colors.grey),
                  ),
                  backgroundColor: active ? Colors.red[100] : Colors.grey[200],
                );
              }).toList(),
            ),
            const SizedBox(height: 16),
          ],

          // Domains with concerns
          if (domains.isNotEmpty) ...[
            const Text('Domains with Concerns',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 6,
              children: domains
                  .map((d) => Chip(
                        label: Text(d.replaceAll('_', ' '),
                            style: const TextStyle(fontSize: 12)),
                        backgroundColor: Colors.orange[100],
                      ))
                  .toList(),
            ),
            const SizedBox(height: 16),
          ],

          // Referral guidance
          if (_loadingReferrals)
            const Center(child: CircularProgressIndicator())
          else if (_referrals.isNotEmpty) ...[
            const Text('Guidance & Next Steps',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
            const SizedBox(height: 8),
            ..._referrals.map((ref) {
              final g = (ref['guidance'] as Map?)?.cast<String, dynamic>() ?? {};
              final actionItems =
                  (g['action_items'] as List?)?.cast<String>() ?? [];
              final specialists =
                  (g['suggested_specialists'] as List?)?.cast<String>() ?? [];

              return Card(
                margin: const EdgeInsets.only(bottom: 12),
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12)),
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(g['heading'] as String? ?? '',
                          style: const TextStyle(
                              fontWeight: FontWeight.bold, fontSize: 15)),
                      const SizedBox(height: 8),
                      Text(g['message'] as String? ?? '',
                          style: const TextStyle(fontSize: 13, height: 1.6)),
                      if (actionItems.isNotEmpty) ...[
                        const SizedBox(height: 12),
                        const Text('WHAT TO DO',
                            style: TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.bold,
                                color: Colors.indigo,
                                letterSpacing: 0.5)),
                        const SizedBox(height: 6),
                        ...actionItems.map((a) => Padding(
                              padding: const EdgeInsets.only(bottom: 5),
                              child: Row(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  const Text('→  ',
                                      style: TextStyle(
                                          color: Colors.indigo,
                                          fontWeight: FontWeight.bold)),
                                  Expanded(
                                      child: Text(a,
                                          style: const TextStyle(fontSize: 13))),
                                ],
                              ),
                            )),
                      ],
                      if (specialists.isNotEmpty) ...[
                        const SizedBox(height: 12),
                        const Text('SUGGESTED SPECIALISTS',
                            style: TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.bold,
                                color: Colors.indigo,
                                letterSpacing: 0.5)),
                        const SizedBox(height: 6),
                        Wrap(
                          spacing: 6,
                          runSpacing: 4,
                          children: specialists
                              .map((s) => Chip(
                                    label: Text(s.replaceAll('_', ' '),
                                        style: const TextStyle(fontSize: 12)),
                                    backgroundColor: Colors.blue[50],
                                  ))
                              .toList(),
                        ),
                      ],
                      const SizedBox(height: 14),
                      if (!_acknowledged)
                        SizedBox(
                          width: double.infinity,
                          child: OutlinedButton.icon(
                            onPressed: () => _acknowledge(ref['id'] as int),
                            icon: const Icon(Icons.check_circle_outline),
                            label: const Text('I understand and will take action'),
                          ),
                        )
                      else
                        const Row(children: [
                          Icon(Icons.check_circle, color: Colors.green),
                          SizedBox(width: 6),
                          Text('Acknowledged',
                              style: TextStyle(
                                  color: Colors.green,
                                  fontWeight: FontWeight.bold)),
                        ]),
                    ],
                  ),
                ),
              );
            }),
          ],

          const SizedBox(height: 12),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.grey[100],
              borderRadius: BorderRadius.circular(8),
            ),
            child: const Text(
              'This tool is for monitoring only — not diagnosis.\nAlways consult a pediatrician with any concerns.',
              style: TextStyle(fontSize: 12, color: Colors.grey),
              textAlign: TextAlign.center,
            ),
          ),
          const SizedBox(height: 40),
        ],
      ),
    );
  }
}
