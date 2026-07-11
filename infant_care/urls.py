from django.urls import path
from .views import FoodIntroductionView, SymptomLogView, HandoverFolderView

urlpatterns = [
    path('allergies/introduce/', FoodIntroductionView.as_view(), name='introduce-food'),
    path('allergies/introduce/<int:log_id>/symptom/', SymptomLogView.as_view(), name='log-symptom'),
    path('child/<int:child_id>/handover/', HandoverFolderView.as_view(), name='handover-folder'),
]