from django.contrib import admin
from .models import TrainingSession, PlayerAttendance

class PlayerAttendanceInline(admin.TabularInline):
    model = PlayerAttendance
    extra = 0

@admin.register(TrainingSession)
class TrainingSessionAdmin(admin.ModelAdmin):
    list_display = ['date', 'duration_minutes', 'training_types']
    inlines = [PlayerAttendanceInline]

admin.site.register(PlayerAttendance)
