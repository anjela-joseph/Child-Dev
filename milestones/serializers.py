from rest_framework import serializers
from .models import MilestoneCategory, MilestoneItem, RedFlag


class MilestoneCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MilestoneCategory
        fields = ('id', 'name', 'domain')


class MilestoneItemSerializer(serializers.ModelSerializer):
    category = MilestoneCategorySerializer(read_only=True)
    domain = serializers.CharField(source='category.domain', read_only=True)

    class Meta:
        model = MilestoneItem
        fields = (
            'id', 'category', 'domain', 'age_group',
            'description', 'severity_if_missed', 'concern_tags',
            'is_red_flag', 'order',
        )


class RedFlagSerializer(serializers.ModelSerializer):
    class Meta:
        model = RedFlag
        fields = ('id', 'description', 'scope', 'concern_tags', 'applies_to_ages')
