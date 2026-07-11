from django.db import models
from accounts.models import ChildProfile
from milestones.models import MilestoneItem, RedFlag


class Assessment(models.Model):
    """One complete milestone check session for a child."""
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    child = models.ForeignKey(ChildProfile, on_delete=models.CASCADE, related_name='assessments')
    age_at_assessment = models.IntegerField()  # snapshot of child's age when taken
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='in_progress')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.child.name} | Age {self.age_at_assessment} | {self.created_at.date()}"


class MilestoneResponse(models.Model):
    """Parent's answer to a single milestone item in an assessment."""
    RESPONSE_CHOICES = [
        ('met', 'Met'),
        ('emerging', 'Emerging / Sometimes'),
        ('not_yet', 'Not Yet'),
        ('concerned', 'Concerned'),
    ]

    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='responses')
    milestone_item = models.ForeignKey(MilestoneItem, on_delete=models.CASCADE)
    response = models.CharField(max_length=10, choices=RESPONSE_CHOICES)
    parent_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('assessment', 'milestone_item')

    def __str__(self):
        return f"{self.assessment} | {self.milestone_item.description[:40]} | {self.response}"


class RedFlagResponse(models.Model):
    """Parent's answer to a red flag question."""
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='red_flag_responses')
    red_flag = models.ForeignKey(RedFlag, on_delete=models.CASCADE)
    is_present = models.BooleanField()  # True = this red flag is present
    parent_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('assessment', 'red_flag')


class RiskScore(models.Model):
    """Calculated result after an assessment is completed."""
    RISK_LEVEL_CHOICES = [
        ('green', 'Green — On Track'),
        ('yellow', 'Yellow — Monitor'),
        ('orange', 'Orange — Suggest Screening'),
        ('red', 'Red — Seek Evaluation'),
    ]

    assessment = models.OneToOneField(Assessment, on_delete=models.CASCADE, related_name='risk_score')
    risk_level = models.CharField(max_length=10, choices=RISK_LEVEL_CHOICES)
    
    # Per-domain breakdown
    social_emotional_score = models.FloatField(default=0)
    language_score = models.FloatField(default=0)
    cognitive_score = models.FloatField(default=0)
    gross_motor_score = models.FloatField(default=0)
    fine_motor_score = models.FloatField(default=0)
    behavior_score = models.FloatField(default=0)

    # Pattern flags (non-diagnostic)
    flags_asd_pattern = models.BooleanField(default=False)
    flags_adhd_pattern = models.BooleanField(default=False)
    flags_dyslexia_pattern = models.BooleanField(default=False)
    flags_ocd_pattern = models.BooleanField(default=False)

    red_flag_triggered = models.BooleanField(default=False)
    domains_with_concerns = models.JSONField(default=list)
    # e.g. ["language_communication", "social_emotional"]

    summary_message = models.TextField(blank=True)
    calculated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.assessment} | {self.risk_level}"
