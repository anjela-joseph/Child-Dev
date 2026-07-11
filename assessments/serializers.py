from rest_framework import serializers
from .models import Assessment, MilestoneResponse, RedFlagResponse, RiskScore
from milestones.serializers import MilestoneItemSerializer, RedFlagSerializer


# ── Read serializers ────────────────────────────────────────────────────────

class MilestoneResponseReadSerializer(serializers.ModelSerializer):
    milestone_item = MilestoneItemSerializer(read_only=True)

    class Meta:
        model = MilestoneResponse
        fields = ('id', 'milestone_item', 'response', 'parent_note')


class RedFlagResponseReadSerializer(serializers.ModelSerializer):
    red_flag = RedFlagSerializer(read_only=True)

    class Meta:
        model = RedFlagResponse
        fields = ('id', 'red_flag', 'is_present', 'parent_note')


class RiskScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiskScore
        fields = (
            'risk_level',
            'social_emotional_score',
            'language_score',
            'cognitive_score',
            'gross_motor_score',
            'fine_motor_score',
            'behavior_score',
            'flags_asd_pattern',
            'flags_adhd_pattern',
            'flags_dyslexia_pattern',
            'flags_ocd_pattern',
            'red_flag_triggered',
            'domains_with_concerns',
            'summary_message',
            'calculated_at',
        )


class AssessmentDetailSerializer(serializers.ModelSerializer):
    responses = MilestoneResponseReadSerializer(many=True, read_only=True)
    red_flag_responses = RedFlagResponseReadSerializer(many=True, read_only=True)
    risk_score = RiskScoreSerializer(read_only=True)

    class Meta:
        model = Assessment
        fields = (
            'id', 'child', 'age_at_assessment', 'status',
            'created_at', 'completed_at',
            'responses', 'red_flag_responses', 'risk_score',
        )


# ── Write serializers ───────────────────────────────────────────────────────

class MilestoneResponseWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = MilestoneResponse
        fields = ('milestone_item', 'response', 'parent_note')


class RedFlagResponseWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = RedFlagResponse
        fields = ('red_flag', 'is_present', 'parent_note')


class SubmitAssessmentSerializer(serializers.Serializer):
    """
    Single payload to submit a completed assessment in one call.
    The Flutter team posts this to /api/assessments/{id}/submit/
    """
    milestone_responses = MilestoneResponseWriteSerializer(many=True)
    red_flag_responses = RedFlagResponseWriteSerializer(many=True, required=False)

    def validate_milestone_responses(self, value):
        if not value:
            raise serializers.ValidationError('At least one milestone response is required.')
        return value


class AssessmentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing assessments."""
    risk_level = serializers.CharField(source='risk_score.risk_level', default=None, read_only=True)

    class Meta:
        model = Assessment
        fields = ('id', 'child', 'age_at_assessment', 'status', 'created_at', 'risk_level')
