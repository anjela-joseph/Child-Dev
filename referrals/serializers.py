from rest_framework import serializers
from .models import ReferralGuidance, AssessmentReferral


class ReferralGuidanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferralGuidance
        fields = (
            'id', 'risk_level', 'concern_tag',
            'heading', 'message', 'action_items', 'suggested_specialists',
        )


class AssessmentReferralSerializer(serializers.ModelSerializer):
    guidance = ReferralGuidanceSerializer(read_only=True)

    class Meta:
        model = AssessmentReferral
        fields = ('id', 'guidance', 'created_at', 'parent_acknowledged', 'acknowledged_at')
