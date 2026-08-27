from django import forms
from version1.teams_app.models import Team
from django import forms
from .models.rating import PlayerPerformancePotentialRating

class ReportFilterForm(forms.Form):
    PERIOD_CHOICES = [
        ('All', 'All'),
        ('This Week', 'This Week'),
        ('This Month', 'This Month'),
        ('This Year', 'This Year'),
    ]
    team = forms.ModelChoiceField(queryset=Team.objects.all(), required=False, label="Team")
    period = forms.ChoiceField(choices=PERIOD_CHOICES, required=False, label="Period")
    start_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))


class PlayerPerformancePotentialRatingForm(forms.ModelForm):

    class Meta:
        model = PlayerPerformancePotentialRating

        fields = ['performance','potential','notes',]
        widgets = {
            'performance': forms.Select(attrs={'class': 'form-select',}),
            'potential': forms.Select(attrs={'class': 'form-select',}),
            'notes': forms.Textarea(attrs={'class': 'form-control','rows': 3,'placeholder': 'Optional notes...',}),
        }