from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, ChildProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'phone', 'is_active', 'created_at')
    list_filter = ('is_active', 'is_staff')
    search_fields = ('email', 'username', 'phone')
    ordering = ('-created_at',)
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Extra', {'fields': ('phone',)}),
    )


@admin.register(ChildProfile)
class ChildProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'date_of_birth', 'age_in_years', 'gender', 'created_at')
    list_filter = ('gender',)
    search_fields = ('name', 'parent__email')
    ordering = ('name',)
    readonly_fields = ('age_in_years', 'created_at', 'updated_at')
