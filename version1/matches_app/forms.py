from django import forms
from .models import Match
from version1.lineup_app.models import MatchLineup, Substitution
from version1.players_app.models import Player


class MatchForm(forms.ModelForm):
    time = forms.TimeField(
        widget=forms.TimeInput(format='%H:%M', attrs={'type': 'time'})
    )

    class Meta:
        model = Match
        fields = '__all__'



class MatchResultForm(forms.ModelForm):

    class Meta:
        model = Match
        fields = ["home_score", "away_score", "result_status",]

        widgets = {
            "home_score": forms.NumberInput(
                attrs={"min": 0,"class": "form-control",}
            ),

            "away_score": forms.NumberInput(
                attrs={"min": 0,"class": "form-control",}
            ),

            "result_status": forms.Select(
                attrs={"class": "form-control",}
            ),
        }

