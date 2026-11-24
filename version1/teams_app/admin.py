from django.contrib import admin
from .models import StaffMember, Team, AgeGroup, Country, Region

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
    list_filter = ['role', 'age_group', 'teams']
    search_fields = ['name', 'teams']

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ['name']
    list_filter = ['name']
    search_fields = ['name']

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ['name', 'country']
    list_filter = ['name', 'country']
    search_fields = ['name', 'country']



