from django import forms
from .models import Match, MatchLineup

class MatchForm(forms.ModelForm):

    time = forms.TimeField(widget=forms.TimeInput(format='%H:%M', attrs={'type': 'time'})),

    class Meta:
        model = Match
        fields = '__all__'

class MatchLineupForm(forms.ModelForm):

    time_entered = forms.TimeField(required=False, widget=forms.TimeInput(format='%H:%M'), input_formats=['%H:%M'])

    class Meta:
        model = MatchLineup
        fields = '__all__'

    
