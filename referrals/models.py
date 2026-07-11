from django.db import models
from assessments.models import RiskScore


class ReferralGuidance(models.Model):
    """Guidance text and specialist suggestions shown after an assessment result."""
    SPECIALIST_CHOICES = [
        ('pediatrician', 'Pediatrician / Family Doctor'),
        ('dev_pediatrician', 'Developmental Pediatrician'),
        ('speech_therapist', 'Speech-Language Pathologist'),
        ('occupational_therapist', 'Occupational Therapist'),
        ('child_psychologist', 'Child Psychologist'),
        ('child_psychiatrist', 'Child Psychiatrist'),
        ('audiologist', 'Audiologist'),
        ('vision', 'Vision Assessment'),
    ]

    TRIGGER_CHOICES = [
        ('green', 'Green'),
        ('yellow', 'Yellow'),
        ('orange', 'Orange'),
        ('red', 'Red'),
    ]

    risk_level = models.CharField(max_length=10, choices=TRIGGER_CHOICES)
    concern_tag = models.CharField(max_length=30, blank=True)
    # blank = applies to all; filled = specific to e.g. "asd", "adhd"

    heading = models.CharField(max_length=200)
    message = models.TextField()
    # screening language only — never diagnostic
    action_items = models.JSONField(default=list)
    # e.g. ["Read and talk daily", "Check hearing if speech is delayed"]
    suggested_specialists = models.JSONField(default=list)
    # list of specialist keys from SPECIALIST_CHOICES

    def __str__(self):
        return f"[{self.risk_level}] {self.heading}"


class AssessmentReferral(models.Model):
    """The actual referral record attached to a completed assessment."""
    risk_score = models.ForeignKey(RiskScore, on_delete=models.CASCADE, related_name='referrals')
    guidance = models.ForeignKey(ReferralGuidance, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    parent_acknowledged = models.BooleanField(default=False)
    acknowledged_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.risk_score.assessment.child.name} | {self.guidance}"
