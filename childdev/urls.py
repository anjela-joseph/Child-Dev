from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    frontend_home,
    child_dashboard_home,
    login_page,
    register_page,
    milestones_page,
    assessments_page,
    care_page,
    referrals_page,
    child_detail_page,
)

urlpatterns = [
    path('', child_dashboard_home, name='child_dashboard_home'),
    path('demo/', frontend_home, name='frontend_home'),
    path('login/', login_page, name='login_page'),
    path('register/', register_page, name='register_page'),
    path('milestones/', milestones_page, name='milestones_page'),
    path('assessments/', assessments_page, name='assessments_page'),
    path('care/', care_page, name='care_page'),
    path('referrals/', referrals_page, name='referrals_page'),
    path('child/<int:child_id>/', child_detail_page, name='child_detail_page'),
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/milestones/', include('milestones.urls')),
    path('api/assessments/', include('assessments.urls')),
    path('api/referrals/', include('referrals.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
