# actions_app/admin.py
from django.contrib import admin
from .models import TeamActionStats

@admin.register(TeamActionStats)
class TeamActionStatsAdmin(admin.ModelAdmin):
    list_display = ('match', 'team_name', 'is_our_team', 'shots_on_target_inside_box', 'shots_off_target_inside_box', 'corners')
    list_filter = ('is_our_team', 'match')
    search_fields = ('team_name',)
    readonly_fields = ('team_name',)
