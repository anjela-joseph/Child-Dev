from django.urls import path
from .views import (
    MilestoneCategoryListView,
    MilestoneItemListView,
    RedFlagListView,
    ChecklistForAgeView,
)

urlpatterns = [
    path('categories/', MilestoneCategoryListView.as_view(), name='milestone-categories'),
    path('items/', MilestoneItemListView.as_view(), name='milestone-items'),
    path('red-flags/', RedFlagListView.as_view(), name='red-flags'),
    path('checklist/', ChecklistForAgeView.as_view(), name='checklist-for-age'),
]
