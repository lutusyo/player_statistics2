from django.contrib import admin
from .models import StaffMember, Team, AgeGroup


@admin.register(AgeGroup)
class AgeGroupAdmin(admin.ModelAdmin):
    search_fields = ['name']


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(StaffMember)
class StaffMemberAdmin(admin.ModelAdmin):
    list_display = ['name', 'role', 'age_group']
    list_filter = ['role', 'age_group']
    search_fields = ['name']