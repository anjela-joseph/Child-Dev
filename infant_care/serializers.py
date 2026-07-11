from rest_framework import serializers
from .models import FoodIntroduction, AllergySymptomLog, HandoverFolder, MedicationRecord

class AllergySymptomLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AllergySymptomLog
        fields = ['id', 'logged_at', 'has_rash', 'has_digestive_issues', 'has_respiratory_issues', 'notes']

class FoodIntroductionSerializer(serializers.ModelSerializer):
    is_buffer_active = serializers.ReadOnlyField()
    symptoms = AllergySymptomLogSerializer(many=True, read_only=True)

    class Meta:
        model = FoodIntroduction
        fields = ['id', 'food_name', 'introduced_at', 'status', 'is_buffer_active', 'symptoms']

class MedicationRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicationRecord
        fields = ['id', 'name', 'dosage', 'frequency', 'instructions']

class HandoverFolderSerializer(serializers.ModelSerializer):
    medications = MedicationRecordSerializer(many=True, read_only=True)
    child_name = serializers.CharField(source='child.name', read_only=True)

    class Meta:
        model = HandoverFolder
        fields = ['child_name', 'blood_group', 'physical_details', 'emergency_instructions', 'updated_at', 'medications']