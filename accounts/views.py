from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import ChildProfile
from .serializers import RegisterSerializer, UserSerializer, ChildProfileSerializer


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class MeView(APIView):
    """Get or update the logged-in parent's profile."""
    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ChildProfileListCreateView(generics.ListCreateAPIView):
    serializer_class = ChildProfileSerializer

    def get_queryset(self):
        return ChildProfile.objects.filter(parent=self.request.user).order_by('name')


class ChildProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ChildProfileSerializer

    def get_queryset(self):
        return ChildProfile.objects.filter(parent=self.request.user)
