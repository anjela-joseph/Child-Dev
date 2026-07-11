from django.contrib import admin
from .models import Assessment, MilestoneResponse, RedFlagResponse, RiskScore


class MilestoneResponseInline(admin.TabularInline):
    model = MilestoneResponse
    extra = 0
    fields = ('milestone_item', 'response', 'parent_note')
    readonly_fields = ('milestone_item',)


class RedFlagResponseInline(admin.TabularInline):
    model = RedFlagResponse
    extra = 0
    fields = ('red_flag', 'is_present', 'parent_note')
    readonly_fields = ('red_flag',)


class RiskScoreInline(admin.StackedInline):
    model = RiskScore
    extra = 0
    readonly_fields = (
        'risk_level',
        'social_emotional_score', 'language_score', 'cognitive_score',
        'gross_motor_score', 'fine_motor_score', 'behavior_score',
        'flags_asd_pattern', 'flags_adhd_pattern',
        'flags_dyslexia_pattern', 'flags_ocd_pattern',
        'red_flag_triggered', 'domains_with_concerns',
        'summary_message', 'calculated_at',
    )
    can_delete = False


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = (
        'get_child_name', 'get_parent_email',
        'age_at_assessment', 'status',
        'get_risk_level', 'created_at'
    )
    list_filter = ('status', 'age_at_assessment', 'risk_score__risk_level')
    search_fields = ('child__name', 'child__parent__email')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'completed_at')
    inlines = [RiskScoreInline, MilestoneResponseInline, RedFlagResponseInline]

    @admin.display(description='Child', ordering='child__name')
    def get_child_name(self, obj):
        return obj.child.name

    @admin.display(description='Parent', ordering='child__parent__email')
    def get_parent_email(self, obj):
        return obj.child.parent.email

    @admin.display(description='Risk Level')
    def get_risk_level(self, obj):
        try:
            level = obj.risk_score.risk_level
            colours = {
                'green': '🟢', 'yellow': '🟡',
                'orange': '🟠', 'red': '🔴'
            }
            return f"{colours.get(level, '')} {level.upper()}"
        except RiskScore.DoesNotExist:
            return '—'


@admin.register(RiskScore)
class RiskScoreAdmin(admin.ModelAdmin):
    list_display = (
        'get_child', 'get_age', 'risk_level',
        'red_flag_triggered',
        'flags_asd_pattern', 'flags_adhd_pattern',
        'flags_dyslexia_pattern', 'flags_ocd_pattern',
        'calculated_at',
    )
    list_filter = (
        'risk_level', 'red_flag_triggered',
        'flags_asd_pattern', 'flags_adhd_pattern',
        'flags_dyslexia_pattern', 'flags_ocd_pattern',
    )
    search_fields = ('assessment__child__name', 'assessment__child__parent__email')
    readonly_fields = ('calculated_at',)

    @admin.display(description='Child')
    def get_child(self, obj):
        return obj.assessment.child.name

    @admin.display(description='Age')
    def get_age(self, obj):
        return obj.assessment.age_at_assessment
