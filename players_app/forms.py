from django import forms
from .models import Player


class PlayerForm(forms.ModelForm):
    birthdate = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )


    class Meta:
        model = Player
        fields = '__all__'
