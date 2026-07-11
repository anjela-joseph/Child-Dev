from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import Assessment, MilestoneResponse, RedFlagResponse
from .serializers import (
    AssessmentListSerializer,
    AssessmentDetailSerializer,
    SubmitAssessmentSerializer,
)
from accounts.models import ChildProfile
from .scoring import calculate_risk_score
from core.permissions import IsChildOwner


class AssessmentListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/assessments/      — list all assessments for this parent's children
    POST /api/assessments/      — start a new assessment { "child": <id> }
    """
    serializer_class = AssessmentListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Assessment.objects.filter(
            child__parent=self.request.user
        ).select_related('child', 'risk_score').order_by('-created_at')

    def perform_create(self, serializer):
        child = get_object_or_404(
            ChildProfile, pk=self.request.data.get('child'), parent=self.request.user
        )
        serializer.save(child=child, age_at_assessment=child.age_in_years)


class AssessmentDetailView(generics.RetrieveAPIView):
    """
    GET /api/assessments/<id>/  — full detail including responses and risk score
    """
    serializer_class = AssessmentDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsChildOwner]

    def get_queryset(self):
        return Assessment.objects.filter(child__parent=self.request.user)


class SubmitAssessmentView(APIView):
    """
    POST /api/assessments/<id>/submit/

    Submit all milestone + red flag responses in one call.
    Triggers scoring and returns the risk score immediately.

    Body:
    {
        "milestone_responses": [
            { "milestone_item": 1, "response": "met", "parent_note": "" },
            ...
        ],
        "red_flag_responses": [
            { "red_flag": 3, "is_present": false },
            ...
        ]
    }
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        assessment = get_object_or_404(
            Assessment, pk=pk, child__parent=request.user
        )

        if assessment.status == 'completed':
            return Response(
                {'error': 'This assessment has already been submitted.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = SubmitAssessmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Save milestone responses (bulk)
        milestone_responses = [
            MilestoneResponse(assessment=assessment, **item)
            for item in data['milestone_responses']
        ]
        MilestoneResponse.objects.bulk_create(milestone_responses, ignore_conflicts=True)

        # Save red flag responses (bulk)
        red_flag_responses = [
            RedFlagResponse(assessment=assessment, **item)
            for item in data.get('red_flag_responses', [])
        ]
        if red_flag_responses:
            RedFlagResponse.objects.bulk_create(red_flag_responses, ignore_conflicts=True)

        # Run scoring
        risk_score = calculate_risk_score(assessment)

        return Response({
            'assessment_id': assessment.id,
            'risk_level': risk_score.risk_level,
            'domains_with_concerns': risk_score.domains_with_concerns,
            'flags': {
                'asd_pattern':        risk_score.flags_asd_pattern,
                'adhd_pattern':       risk_score.flags_adhd_pattern,
                'dyslexia_pattern':   risk_score.flags_dyslexia_pattern,
                'ocd_pattern':        risk_score.flags_ocd_pattern,
                'red_flag_triggered': risk_score.red_flag_triggered,
            },
            'summary_message': risk_score.summary_message,
        }, status=status.HTTP_200_OK)


class ChildAssessmentHistoryView(generics.ListAPIView):
    """
    GET /api/assessments/child/<child_id>/history/
    All completed assessments for a child in chronological order.
    Used to show progress over time.
    """
    serializer_class = AssessmentListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        child_id = self.kwargs['child_id']
        return Assessment.objects.filter(
            child__id=child_id,
            child__parent=self.request.user,
            status='completed',
        ).select_related('risk_score').order_by('created_at')
