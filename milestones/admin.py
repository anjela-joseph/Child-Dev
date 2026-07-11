from django.contrib import admin
from .models import MilestoneCategory, MilestoneItem, RedFlag


@admin.register(MilestoneCategory)
class MilestoneCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'domain')
    list_filter = ('domain',)
    ordering = ('domain',)


class MilestoneItemInline(admin.TabularInline):
    model = MilestoneItem
    extra = 0
    fields = ('age_group', 'description', 'severity_if_missed', 'concern_tags', 'order')
    ordering = ('age_group', 'order')


@admin.register(MilestoneItem)
class MilestoneItemAdmin(admin.ModelAdmin):
    list_display = (
        'age_group', 'get_domain', 'short_description',
        'severity_if_missed', 'is_red_flag', 'order'
    )
    list_filter = ('age_group', 'category__domain', 'severity_if_missed', 'is_red_flag')
    search_fields = ('description',)
    ordering = ('age_group', 'category__domain', 'order')

    @admin.display(description='Domain', ordering='category__domain')
    def get_domain(self, obj):
        return obj.category.get_domain_display()

    @admin.display(description='Milestone')
    def short_description(self, obj):
        return obj.description[:80]


@admin.register(RedFlag)
class RedFlagAdmin(admin.ModelAdmin):
    list_display = ('short_description', 'scope', 'concern_tags', 'applies_to_ages')
    list_filter = ('scope',)
    search_fields = ('description',)

    @admin.display(description='Description')
    def short_description(self, obj):
        return obj.description[:80]
