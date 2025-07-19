# announcements_app/admin.py

from django.contrib import admin
from .models import Announcement, PlanItem

class PlanItemInline(admin.TabularInline):
    model = PlanItem
    extra = 1

class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'age_group', 'date_for', 'created_at')
    inlines = [PlanItemInline]

admin.site.register(Announcement, AnnouncementAdmin)
