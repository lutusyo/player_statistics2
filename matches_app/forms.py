from django import forms
from .models import MatchLineup

class MatchLineupForm(forms.ModelForm):
    class Meta:
        model = MatchLineup
        fields = '__all__'
        widgets = {
            'time_entered': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
        }
