from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import AssessmentReferral, ReferralGuidance
from .serializers import AssessmentReferralSerializer, ReferralGuidanceSerializer
from assessments.models import Assessment


class AssessmentReferralView(generics.ListAPIView):
    """
    GET /api/referrals/assessment/<assessment_id>/
    Returns the referral guidance for a completed assessment.
    """
    serializer_class = AssessmentReferralSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        assessment_id = self.kwargs['assessment_id']
        return AssessmentReferral.objects.filter(
            risk_score__assessment__id=assessment_id,
            risk_score__assessment__child__parent=self.request.user,
        ).select_related('guidance')


class AcknowledgeReferralView(APIView):
    """
    POST /api/referrals/<id>/acknowledge/
    Parent marks that they have read and understood the referral guidance.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        referral = get_object_or_404(
            AssessmentReferral,
            pk=pk,
            risk_score__assessment__child__parent=request.user
        )
        referral.parent_acknowledged = True
        referral.acknowledged_at = timezone.now()
        referral.save(update_fields=['parent_acknowledged', 'acknowledged_at'])
        return Response({'acknowledged': True})
