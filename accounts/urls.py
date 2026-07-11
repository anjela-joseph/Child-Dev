from django.urls import path
from .views import RegisterView, MeView, ChildProfileListCreateView, ChildProfileDetailView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('me/', MeView.as_view(), name='me'),
    path('children/', ChildProfileListCreateView.as_view(), name='children-list'),
    path('children/<int:pk>/', ChildProfileDetailView.as_view(), name='children-detail'),
]
