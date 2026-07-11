from django.contrib import admin
from .models import ReferralGuidance, AssessmentReferral


@admin.register(ReferralGuidance)
class ReferralGuidanceAdmin(admin.ModelAdmin):
    list_display = ('heading', 'risk_level', 'concern_tag')
    list_filter = ('risk_level', 'concern_tag')
    search_fields = ('heading', 'message')
    ordering = ('risk_level', 'concern_tag')


@admin.register(AssessmentReferral)
class AssessmentReferralAdmin(admin.ModelAdmin):
    list_display = (
        'get_child', 'get_risk_level', 'get_guidance_heading',
        'parent_acknowledged', 'created_at'
    )
    list_filter = ('parent_acknowledged', 'risk_score__risk_level')
    search_fields = ('risk_score__assessment__child__name',)
    readonly_fields = ('created_at', 'acknowledged_at')

    @admin.display(description='Child')
    def get_child(self, obj):
        return obj.risk_score.assessment.child.name

    @admin.display(description='Risk Level')
    def get_risk_level(self, obj):
        return obj.risk_score.risk_level.upper()

    @admin.display(description='Guidance')
    def get_guidance_heading(self, obj):
        return obj.guidance.heading if obj.guidance else '—'
