from django.urls import path
from .views import (
    AssessmentListCreateView,
    AssessmentDetailView,
    SubmitAssessmentView,
    ChildAssessmentHistoryView,
)

urlpatterns = [
    path('', AssessmentListCreateView.as_view(), name='assessment-list'),
    path('<int:pk>/', AssessmentDetailView.as_view(), name='assessment-detail'),
    path('<int:pk>/submit/', SubmitAssessmentView.as_view(), name='assessment-submit'),
    path('child/<int:child_id>/history/', ChildAssessmentHistoryView.as_view(), name='assessment-history'),
]
