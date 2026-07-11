from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny  # 🌟 ADD THIS IMPORT
from django.shortcuts import get_object_or_404
from accounts.models import ChildProfile
from .models import FoodIntroduction, HandoverFolder, AllergySymptomLog
from .serializers import FoodIntroductionSerializer, AllergySymptomLogSerializer, HandoverFolderSerializer

# --- 3-DAY ALLERGY BUFFER ENGINE ---
class FoodIntroductionView(APIView):
    permission_classes = [AllowAny]  # 🌟 ADD THIS LINE AT THE TOP OF THE CLASS
    
    def get(self, request):
        child_id = request.query_params.get('child_id')
        logs = FoodIntroduction.objects.filter(child_id=child_id).order_by('-introduced_at')
        serializer = FoodIntroductionSerializer(logs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = FoodIntroductionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SymptomLogView(APIView):
    permission_classes = [AllowAny]  # 🌟 ADD THIS LINE TOO
    
    def post(self, request, log_id):
        introduction = get_object_or_404(FoodIntroduction, id=log_id)
        serializer = AllergySymptomLogSerializer(data=request.data)
        if serializer.is_valid():
            symptom = serializer.save(introduction=introduction)
            if symptom.has_rash or symptom.has_digestive_issues or symptom.has_respiratory_issues:
                introduction.status = 'reaction'
                introduction.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# --- CAREGIVER HANDOVER DASHBOARD ---
class HandoverFolderView(APIView):
    permission_classes = [AllowAny]  # 🌟 ADD THIS LINE TOO
    
    def get(self, request, child_id):
        child = get_object_or_404(ChildProfile, id=child_id)
        folder, _ = HandoverFolder.objects.get_or_create(child=child)
        danger_foods = FoodIntroduction.objects.filter(child=child, status='reaction').values_list('food_name', flat=True)
        serializer = HandoverFolderSerializer(folder)
        custom_payload = serializer.data
        custom_payload['CRITICAL_ALLERGY_REACTIONS'] = list(danger_foods)
        return Response(custom_payload, status=status.HTTP_200_OK)