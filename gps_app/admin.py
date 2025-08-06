from django.contrib import admin
from .models import GPSRecord
from matches_app.models import MatchLineup

@admin.register(GPSRecord)
class GPSRecordAdmin(admin.ModelAdmin):
    list_display = ('player', 'match', 'sprint_distance', 'player_load')
    list_filter = ('match', 'player')