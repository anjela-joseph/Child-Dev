from django.urls import path
from .views import AssessmentReferralView, AcknowledgeReferralView

urlpatterns = [
    path('assessment/<int:assessment_id>/', AssessmentReferralView.as_view(), name='assessment-referral'),
    path('<int:pk>/acknowledge/', AcknowledgeReferralView.as_view(), name='referral-acknowledge'),
]
