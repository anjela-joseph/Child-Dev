"""
Scoring engine for child development assessments.

Rules:
  Response scores per item:
    met       → 0  (no concern)
    emerging  → 1  (minor concern)
    not_yet   → 2  (concern)
    concerned → 3  (strong concern)

  Per-domain score = average response score across items in that domain (0.0 – 3.0)

  Overall risk level:
    green  → no red flags AND all domain averages < 1.0
    yellow → no red flags AND exactly one domain average >= 1.0 (isolated miss)
    orange → no red flags AND two+ domains >= 1.0, OR any high-severity item missed
    red    → any red flag present, OR any item with severity="high" scored 2+,
             OR regression reported

  Condition pattern flags (non-diagnostic):
    asd_pattern      → 3+ items tagged "asd" scored 2+ across social/language/cognitive
    adhd_pattern     → 3+ items tagged "adhd" scored 2+
    dyslexia_pattern → 2+ items tagged "dyslexia" scored 2+ (ages 5-7)
    ocd_pattern      → 2+ items tagged "ocd" scored 2+

IMPORTANT: This engine never uses diagnostic language. It flags patterns only.
"""

from django.utils import timezone
from collections import defaultdict


RESPONSE_SCORE = {
    'met': 0,
    'emerging': 1,
    'not_yet': 2,
    'concerned': 3,
}

DOMAIN_TO_SCORE_FIELD = {
    'social_emotional':      'social_emotional_score',
    'language_communication': 'language_score',
    'cognitive':             'cognitive_score',
    'gross_motor':           'gross_motor_score',
    'fine_motor':            'fine_motor_score',
    'behavior_attention':    'behavior_score',
}

SUMMARY_MESSAGES = {
    'green': (
        "Great news — your child is meeting most milestones for their age. "
        "Keep doing what you're doing: read together, encourage play with peers, "
        "and keep routines predictable. Check in again at the next age milestone."
    ),
    'yellow': (
        "Your child is doing well overall, with one area to keep an eye on. "
        "This is not a cause for alarm — many children develop at slightly different paces. "
        "We suggest revisiting this checklist in 4–6 weeks. If the concern persists, "
        "speak with your pediatrician."
    ),
    'orange': (
        "There are some areas where your child may benefit from closer monitoring. "
        "We recommend discussing these results with your child's pediatrician or a "
        "developmental specialist. Early support can make a real difference."
    ),
    'red': (
        "Some of your answers suggest your child may benefit from a professional evaluation soon. "
        "This does not mean something is definitely wrong — but it is important to speak with "
        "a developmental pediatrician or specialist as soon as possible. Early evaluation "
        "leads to earlier support."
    ),
}


def calculate_risk_score(assessment):
    """
    Main entry point. Pass a completed Assessment instance.
    Creates or updates its RiskScore and returns it.
    """
    from assessments.models import RiskScore

    milestone_responses = assessment.responses.select_related(
        'milestone_item', 'milestone_item__category'
    ).all()

    red_flag_responses = assessment.red_flag_responses.select_related('red_flag').all()

    # ── 1. Check red flags ──────────────────────────────────────────────────
    red_flag_triggered = any(r.is_present for r in red_flag_responses)

    # ── 2. Per-domain scoring ───────────────────────────────────────────────
    domain_scores_raw = defaultdict(list)   # domain → [numeric scores]
    concern_tags_hit = defaultdict(int)     # tag → count of items scored 2+

    high_severity_missed = False

    for resp in milestone_responses:
        item = resp.milestone_item
        score = RESPONSE_SCORE.get(resp.response, 0)
        domain = item.category.domain
        domain_scores_raw[domain].append(score)

        if score >= 2:
            for tag in (item.concern_tags or []):
                concern_tags_hit[tag] += 1

            if item.severity_if_missed == 'high' and score >= 2:
                high_severity_missed = True

    # Average per domain (0.0–3.0)
    domain_averages = {
        domain: (sum(scores) / len(scores)) if scores else 0.0
        for domain, scores in domain_scores_raw.items()
    }

    domains_with_concerns = [
        domain for domain, avg in domain_averages.items() if avg >= 1.0
    ]

    # ── 3. Overall risk level ───────────────────────────────────────────────
    if red_flag_triggered or high_severity_missed:
        risk_level = 'red'
    elif len(domains_with_concerns) >= 2:
        risk_level = 'orange'
    elif len(domains_with_concerns) == 1:
        risk_level = 'yellow'
    else:
        risk_level = 'green'

    # ── 4. Condition pattern flags ──────────────────────────────────────────
    age = assessment.age_at_assessment

    flags_asd = concern_tags_hit.get('asd', 0) >= 3
    flags_adhd = concern_tags_hit.get('adhd', 0) >= 3
    flags_dyslexia = age >= 5 and concern_tags_hit.get('dyslexia', 0) >= 2
    flags_ocd = concern_tags_hit.get('ocd', 0) >= 2

    # If any pattern flag is set, escalate risk level to at least orange
    if any([flags_asd, flags_adhd, flags_dyslexia, flags_ocd]):
        if risk_level == 'green':
            risk_level = 'yellow'
        if risk_level == 'yellow' and concern_tags_hit.get('asd', 0) >= 3:
            risk_level = 'orange'

    # ── 5. Build / update RiskScore ─────────────────────────────────────────
    risk_score, _ = RiskScore.objects.update_or_create(
        assessment=assessment,
        defaults={
            'risk_level': risk_level,
            'social_emotional_score': domain_averages.get('social_emotional', 0.0),
            'language_score':         domain_averages.get('language_communication', 0.0),
            'cognitive_score':        domain_averages.get('cognitive', 0.0),
            'gross_motor_score':      domain_averages.get('gross_motor', 0.0),
            'fine_motor_score':       domain_averages.get('fine_motor', 0.0),
            'behavior_score':         domain_averages.get('behavior_attention', 0.0),
            'flags_asd_pattern':      flags_asd,
            'flags_adhd_pattern':     flags_adhd,
            'flags_dyslexia_pattern': flags_dyslexia,
            'flags_ocd_pattern':      flags_ocd,
            'red_flag_triggered':     red_flag_triggered,
            'domains_with_concerns':  domains_with_concerns,
            'summary_message':        SUMMARY_MESSAGES[risk_level],
        }
    )

    # Mark assessment complete
    assessment.status = 'completed'
    assessment.completed_at = timezone.now()
    assessment.save(update_fields=['status', 'completed_at'])

    # Attach referral guidance
    _attach_referral(risk_score, flags_asd, flags_adhd, flags_dyslexia, flags_ocd)

    return risk_score


def _attach_referral(risk_score, flags_asd, flags_adhd, flags_dyslexia, flags_ocd):
    """
    Find the best-matching ReferralGuidance and create an AssessmentReferral.
    Priority: condition-specific guidance > general risk-level guidance.
    """
    from referrals.models import ReferralGuidance, AssessmentReferral

    concern_tag = ''
    if flags_asd:
        concern_tag = 'asd'
    elif flags_adhd:
        concern_tag = 'adhd'
    elif flags_dyslexia:
        concern_tag = 'dyslexia'
    elif flags_ocd:
        concern_tag = 'ocd'

    # Try condition-specific first, then fall back to general
    guidance = None
    if concern_tag:
        guidance = ReferralGuidance.objects.filter(
            risk_level=risk_score.risk_level,
            concern_tag=concern_tag
        ).first()

    if not guidance:
        guidance = ReferralGuidance.objects.filter(
            risk_level=risk_score.risk_level,
            concern_tag=''
        ).first()

    if guidance:
        AssessmentReferral.objects.get_or_create(
            risk_score=risk_score,
            defaults={'guidance': guidance}
        )
