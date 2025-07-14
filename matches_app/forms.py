from django import forms
from .models import Goal, Match
from players_app.models import Player

class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ['match', 'scorer', 'assist_by', 'minute', 'is_own_goal']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Filter players based on match team
        if 'match' in self.initial:
            match = self.initial['match']
        elif self.instance.pk:
            match = self.instance.match
        else:
            match = None

        if match:
            # Limit scorer and assist options to players from this match's team
            team_players = Player.objects.filter(
                playermatchstats__match=match
            ).distinct()
            self.fields['scorer'].queryset = team_players
            self.fields['assist_by'].queryset = team_players

    def clean(self):
        cleaned_data = super().clean()
        is_own_goal = cleaned_data.get('is_own_goal')
        scorer = cleaned_data.get('scorer')
        assist_by = cleaned_data.get('assist_by')

        if is_own_goal:
            # Don't allow assist or scorer for own goals
            cleaned_data['scorer'] = None
            cleaned_data['assist_by'] = None
        return cleaned_data
