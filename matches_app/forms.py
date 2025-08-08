from django import forms
from .models import Match, MatchLineup
from players_app.models import Player


class MatchForm(forms.ModelForm):
    time = forms.TimeField(
        widget=forms.TimeInput(format='%H:%M', attrs={'type': 'time'})
    )

    class Meta:
        model = Match
        fields = '__all__'


class MatchLineupForm(forms.ModelForm):
    time_entered = forms.TimeField(
        required=False,
        widget=forms.TimeInput(format='%H:%M'),
        input_formats=['%H:%M']
    )

    pod_number = forms.CharField(
        required=False,
        label="Pod Number",
        help_text="Optional: Assign Catapult pod number (e.g., Demo 2)",
        widget=forms.TextInput(attrs={'placeholder': 'e.g., Demo 2'})
    )

    class Meta:
        model = MatchLineup
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False


        # ✅ Make all fields optional
        for field in self.fields.values():
            field.required = False

        # Filter players based on selected match
        if 'match' in self.data:
            try:
                match_id = int(self.data.get('match'))
                match = Match.objects.get(id=match_id)
                self.fields['player'].queryset = Player.objects.filter(team__in=[match.home_team, match.away_team])
            except (ValueError, Match.DoesNotExist):
                pass
        elif self.instance.pk and self.instance.match:
            match = self.instance.match
            self.fields['player'].queryset = Player.objects.filter(team__in=[match.home_team, match.away_team])

        # Help texts
        self.fields['is_starting'].help_text = "Tick this for Starting XI"
        self.fields['position'].help_text = "Select playing position"
        self.fields['time_entered'].help_text = "Only fill if this is a substitute"
