from django import forms
from .models import Match, MatchLineup
from players_app.models import Player  # Make sure Player is imported

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

    class Meta:
        model = MatchLineup
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(MatchLineupForm, self).__init__(*args, **kwargs)

        # If a match is selected (e.g. from a dropdown during creation)
        if 'match' in self.data:
            try:
                match_id = int(self.data.get('match'))
                from matches_app.models import Match
                match = Match.objects.get(id=match_id)
                self.fields['player'].queryset = Player.objects.filter(team__in=[match.home_team, match.away_team])
            except (ValueError, Match.DoesNotExist):
                pass
        elif self.instance.pk:
            # Editing an existing lineup entry
            match = self.instance.match
            self.fields['player'].queryset = Player.objects.filter(team__in=[match.home_team, match.away_team])

        # Help texts
        self.fields['is_starting'].help_text = "Tick this for Starting XI"
        self.fields['position'].help_text = "Select playing position"
        self.fields['time_entered'].help_text = "Only fill if this is a substitute"
