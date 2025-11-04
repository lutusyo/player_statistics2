from django import forms
from teams_app.models import Team

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
