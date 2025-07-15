# team_app/admin.py
from django.contrib import admin
from .models import staffMember


@admin.register(staffMember)
class StaffMemberAdmin(admin.ModelAdmin):
    list_display = ['name', 'role', 'age_group']
    list_filter = ['role', 'age_group']
    search_fields = ['name']
