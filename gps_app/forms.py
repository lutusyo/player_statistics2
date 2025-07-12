from django import forms
from matches_app.models import Match

class GPSUploadForm(forms.Form):
    match = forms.ModelChoiceField(queryset=Match.objects.all())
    csv_file = forms.FileField(label="Upload GPS CSV")
