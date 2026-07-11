from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from .models import MilestoneItem, RedFlag, MilestoneCategory
from .serializers import MilestoneItemSerializer, RedFlagSerializer, MilestoneCategorySerializer


class MilestoneCategoryListView(generics.ListAPIView):
    """All milestone domains/categories."""
    queryset = MilestoneCategory.objects.all()
    serializer_class = MilestoneCategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class MilestoneItemListView(generics.ListAPIView):
    """
    All milestone items. Filter by age_group and/or domain.
    GET /api/milestones/items/?age_group=4
    GET /api/milestones/items/?age_group=5&domain=language_communication
    """
    serializer_class = MilestoneItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['age_group', 'category__domain']

    def get_queryset(self):
        return MilestoneItem.objects.filter(
            is_red_flag=False
        ).select_related('category').order_by('age_group', 'category__domain', 'order')


class RedFlagListView(generics.ListAPIView):
    """
    Red flag questions. Filter by age to get only age-relevant ones.
    GET /api/milestones/red-flags/?age=4
    """
    serializer_class = RedFlagSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = RedFlag.objects.all()
        age = self.request.query_params.get('age')
        if age:
            try:
                age = int(age)
                qs = [rf for rf in qs if age in rf.applies_to_ages]
            except ValueError:
                pass
        return qs


class ChecklistForAgeView(APIView):
    """
    Single endpoint that returns everything the Flutter team needs
    to render the full checklist for a given child age.

    GET /api/milestones/checklist/?age=5

    Response:
    {
        "age": 5,
        "categories": [...],
        "milestones": [...],   // grouped by domain
        "red_flags": [...]
    }
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        age = request.query_params.get('age')
        if not age:
            return Response({'error': 'age query param is required.'}, status=400)

        try:
            age = int(age)
        except ValueError:
            return Response({'error': 'age must be an integer between 3 and 7.'}, status=400)

        if age not in range(3, 8):
            return Response({'error': 'age must be between 3 and 7.'}, status=400)

        milestones = MilestoneItem.objects.filter(
            age_group=age, is_red_flag=False
        ).select_related('category').order_by('category__domain', 'order')

        red_flags = [rf for rf in RedFlag.objects.all() if age in rf.applies_to_ages]

        # Group milestones by domain
        grouped = {}
        for item in milestones:
            domain = item.category.domain
            if domain not in grouped:
                grouped[domain] = {
                    'domain': domain,
                    'domain_label': item.category.name,
                    'items': []
                }
            grouped[domain]['items'].append(MilestoneItemSerializer(item).data)

        return Response({
            'age': age,
            'milestone_domains': list(grouped.values()),
            'red_flags': RedFlagSerializer(red_flags, many=True).data,
        })
