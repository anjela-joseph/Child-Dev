from django.db import models


class MilestoneCategory(models.Model):
    """e.g. Social & Emotional, Language & Communication, Cognitive, Physical & Motor"""
    DOMAIN_CHOICES = [
        ('social_emotional', 'Social & Emotional'),
        ('language_communication', 'Language & Communication'),
        ('cognitive', 'Cognitive / Early Learning'),
        ('gross_motor', 'Gross Motor'),
        ('fine_motor', 'Fine Motor & Self-Help'),
        ('behavior_attention', 'Behavior & Attention'),
    ]

    name = models.CharField(max_length=100)
    domain = models.CharField(max_length=30, choices=DOMAIN_CHOICES)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Milestone Categories'

    def __str__(self):
        return f"{self.get_domain_display()}"


class MilestoneItem(models.Model):
    """A single checkable milestone for a specific age group and domain."""
    AGE_CHOICES = [(i, f'Age {i}') for i in range(3, 8)]  # 3, 4, 5, 6, 7

    CONCERN_TAG_CHOICES = [
        ('asd', 'Autism Spectrum'),
        ('adhd', 'ADHD'),
        ('dyslexia', 'Dyslexia / Reading Risk'),
        ('ocd', 'OCD'),
        ('language_delay', 'Language Delay'),
        ('motor_delay', 'Motor Delay'),
        ('social_delay', 'Social Delay'),
        ('general', 'General Development'),
    ]

    SEVERITY_CHOICES = [
        ('low', 'Low — monitor'),
        ('medium', 'Medium — recheck soon'),
        ('high', 'High — seek evaluation'),
    ]

    category = models.ForeignKey(MilestoneCategory, on_delete=models.CASCADE, related_name='items')
    age_group = models.IntegerField(choices=AGE_CHOICES)
    description = models.TextField()
    severity_if_missed = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='low')
    concern_tags = models.JSONField(default=list, blank=True)
    # e.g. ["asd", "language_delay"]
    is_red_flag = models.BooleanField(default=False)
    # True = this is a standalone red flag, not a standard milestone
    order = models.PositiveIntegerField(default=0)
    target_age_months = models.IntegerField(null=True, blank=True, help_text="Specific month for ages 0-2")
    video_url = models.URLField(blank=True, null=True, help_text="Reference video for new parents")
    exercise_guidance = models.TextField(blank=True, help_text="Gentle activities if milestone is missed")

    class Meta:
        ordering = ['age_group', 'category__domain', 'order']

    def __str__(self):
        return f"Age {self.age_group} | {self.category.get_domain_display()} | {self.description[:60]}"


class RedFlag(models.Model):
    """Standalone red flags that trigger immediate escalation regardless of milestone score."""
    SCOPE_CHOICES = [
        ('global', 'Global'),
        ('social_communication', 'Social & Communication'),
        ('motor', 'Motor & Physical'),
        ('learning', 'Learning & School Readiness'),
        ('behavior', 'Emotional & Behavior'),
    ]

    description = models.TextField()
    scope = models.CharField(max_length=30, choices=SCOPE_CHOICES)
    concern_tags = models.JSONField(default=list, blank=True)
    applies_to_ages = models.JSONField(default=list, blank=True)
    # e.g. [3, 4, 5, 6, 7] or [3, 4] for age-specific flags

    def __str__(self):
        return f"[{self.get_scope_display()}] {self.description[:80]}"
