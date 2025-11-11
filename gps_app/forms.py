from django import forms

class GPSUploadForm(forms.Form):
    csv_file = forms.FileField(label="Upload CSV file")
