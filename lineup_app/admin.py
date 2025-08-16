from django.contrib import admin
from django import forms
from django.shortcuts import render, redirect
from django.urls import path, reverse
from django.utils.html import format_html
from django.contrib import messages
from django.forms import modelformset_factory

from lineup_app.models import Match, MatchLineup, Substitution
from matches_app.admin import MatchAdmin
from lineup_app.forms import MatchLineupForm
from players_app.models import Player

### Bulk Lineup Form ###
class MatchLineupBulkForm(forms.ModelForm):
    class Meta:
        model = MatchLineup
        # Changed 'time_entered' -> 'time_in' to match your model
        fields = ['match', 'player', 'position', 'pod_number', 'is_starting', 'time_in']

    def __init__(self, *args, **kwargs):
        match = kwargs.pop('match', None)
        super().__init__(*args, **kwargs)
        if match:
            self.initial['match'] = match
            self.fields['match'].initial = match
            self.fields['match'].widget = forms.HiddenInput()
            # Set initial time_in to 0 or use match.time.hour/minute if appropriate
            self.fields['time_in'].initial = 0  
            self.fields['pod_number'].initial = "Demo 2"  # default for new entries

            # Filter players by age groups of both teams
            home_age_group = match.home_team.age_group
            away_age_group = match.away_team.age_group
            self.fields['player'].queryset = Player.objects.filter(age_group__in=[home_age_group, away_age_group])


### Lineup Admin ###
class MatchLineupAdmin(admin.ModelAdmin):
    form = MatchLineupForm
    list_display = ['match', 'player', 'position', 'is_starting']
    list_filter = ['match', 'team', 'is_starting']
    search_fields = ['player__name']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('match', 'player', 'team')
    

# Register Models
admin.site.register(MatchLineup, MatchLineupAdmin)
admin.site.register(Substitution)