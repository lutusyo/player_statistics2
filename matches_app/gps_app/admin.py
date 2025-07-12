from django.contrib import admin
from .models import GPSRecord, PodAssignment

@admin.register(GPSRecord)
class GPSRecordAdmin(admin.ModelAdmin):
    list_display = ('player', 'match', 'sprint_distance', 'player_load')
    list_filter = ('match', 'player')

@admin.register(PodAssignment)
class PodAssignmentAdmin(admin.ModelAdmin):
    list_display = ('match', 'pod_number', 'player')
    list_filter = ('match', 'player')
