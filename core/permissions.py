"""
Reusable permission classes for the childdev backend.

All API views are authenticated by default (set in settings.py REST_FRAMEWORK).
These classes add object-level checks on top of that.
"""

from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwner(BasePermission):
    """
    Allow access only if the object belongs to the requesting user.
    The object must have a direct `parent` or `user` field pointing to the user.

    Usage:
        class ChildProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
            permission_classes = [IsAuthenticated, IsOwner]
    """
    message = 'You do not have permission to access this resource.'

    def has_object_permission(self, request, view, obj):
        # Support objects with a direct parent or user FK
        if hasattr(obj, 'parent'):
            return obj.parent == request.user
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return False


class IsChildOwner(BasePermission):
    """
    Allow access only if the object's child belongs to the requesting user.
    Used for Assessment, RiskScore, AssessmentReferral etc.

    Usage:
        class AssessmentDetailView(generics.RetrieveAPIView):
            permission_classes = [IsAuthenticated, IsChildOwner]
    """
    message = 'You do not have permission to access this child\'s data.'

    def has_object_permission(self, request, view, obj):
        # Direct child FK (Assessment)
        if hasattr(obj, 'child'):
            return obj.child.parent == request.user
        # Via assessment (RiskScore)
        if hasattr(obj, 'assessment'):
            return obj.assessment.child.parent == request.user
        # Via risk_score (AssessmentReferral)
        if hasattr(obj, 'risk_score'):
            return obj.risk_score.assessment.child.parent == request.user
        return False


class IsReadOnly(BasePermission):
    """
    Allow read-only access (GET, HEAD, OPTIONS) to any authenticated user.
    Used for milestone and red flag list endpoints — parents can read but not modify.
    """
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class IsOwnerOrReadOnly(BasePermission):
    """
    Allow full access to the owner, read-only to everyone else.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if hasattr(obj, 'parent'):
            return obj.parent == request.user
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return False
