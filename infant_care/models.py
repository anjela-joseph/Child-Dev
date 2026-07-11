from django.db import models
from django.utils import timezone
from datetime import timedelta
from accounts.models import ChildProfile

# --- ALLERGY BUFFER ENGINE ---
class FoodIntroduction(models.Model):
    STATUS_CHOICES = [
        ('testing', 'Testing (3-Day Buffer)'),
        ('safe', 'Safe / Verified'),
        ('reaction', 'Allergic Reaction Detected'),
    ]
    child = models.ForeignKey(ChildProfile, on_delete=models.CASCADE, related_name='food_introductions')
    food_name = models.CharField(max_length=100)
    introduced_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='testing')

    @property
    def is_buffer_active(self):
        """Returns True if the food was introduced less than 72 hours ago."""
        if self.status != 'testing':
            return False
        return timezone.now() < self.introduced_at + timedelta(days=3)

class AllergySymptomLog(models.Model):
    introduction = models.ForeignKey(FoodIntroduction, on_delete=models.CASCADE, related_name='symptoms')
    logged_at = models.DateTimeField(auto_now_add=True)
    has_rash = models.BooleanField(default=False)
    has_digestive_issues = models.BooleanField(default=False)
    has_respiratory_issues = models.BooleanField(default=False)
    notes = models.TextField(blank=True)


# --- CAREGIVER HANDOVER FOLDER ---
class HandoverFolder(models.Model):
    child = models.OneToOneField(ChildProfile, on_delete=models.CASCADE, related_name='handover_folder')
    blood_group = models.CharField(max_length=5, blank=True)
    physical_details = models.TextField(blank=True, help_text="Sleeping routines, physical marks, etc.")
    emergency_instructions = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

class MedicationRecord(models.Model):
    folder = models.ForeignKey(HandoverFolder, on_delete=models.CASCADE, related_name='medications')
    name = models.CharField(max_length=100)
    dosage = models.CharField(max_length=50)
    frequency = models.CharField(max_length=100)
    instructions = models.TextField(blank=True)
