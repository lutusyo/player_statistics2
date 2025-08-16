from django import forms
from .models import Match
from lineup_app.models import MatchLineup, Substitution
from players_app.models import Player


class MatchForm(forms.ModelForm):
    time = forms.TimeField(
        widget=forms.TimeInput(format='%H:%M', attrs={'type': 'time'})
    )

    class Meta:
        model = Match
        fields = '__all__'

