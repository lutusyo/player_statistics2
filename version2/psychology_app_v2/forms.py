from django import forms
from version2.psychology_app_v2.models import Assessment
from version1.players_app.models import Player


class UploadExcelForm(forms.Form):
    file = forms.FileField()

from django import forms

from version2.psychology_app_v2.models import Assessment
from version1.players_app.models import Player
from version1.teams_app.models import AgeGroup, Team


class AssessmentForm(forms.ModelForm):

    age_group = forms.ModelChoiceField(
        queryset=AgeGroup.objects.all().order_by('name'),
        required=False,
        empty_label="All Age Groups"
    )

    team = forms.ModelChoiceField(
        queryset=Team.objects.all().order_by('name'),
        required=False,
        empty_label="All Teams"
    )

    class Meta:
        model = Assessment

        fields = [
            'age_group',
            'team',
            'player',
            'start_date',
            'end_date',
            'task',
            'iq_range',
            'cognitive_percent',
            'personality_percent',
            'neuro_psychology_percent',
            'education_percent',
        ]

        widgets = {
            'start_date': forms.DateInput(
                attrs={
                    'type': 'date'
                }
            ),

            'end_date': forms.DateInput(
                attrs={
                    'type': 'date'
                }
            ),

            'iq_range': forms.NumberInput(
                attrs={
                    'placeholder': 'Enter IQ'
                }
            ),

            'cognitive_percent': forms.NumberInput(
                attrs={
                    'placeholder': 'Cognitive %',
                    'step': '0.01',
                    'min': '0',
                    'max': '100',
                }
            ),

            'personality_percent': forms.NumberInput(
                attrs={
                    'placeholder': 'Personality %',
                    'step': '0.01',
                    'min': '0',
                    'max': '100',
                }
            ),

            'neuro_psychology_percent': forms.NumberInput(
                attrs={
                    'placeholder': 'Neuro Psychology %',
                    'step': '0.01',
                    'min': '0',
                    'max': '100',
                }
            ),

            'education_percent': forms.NumberInput(
                attrs={
                    'placeholder': 'Education %',
                    'step': '0.01',
                    'min': '0',
                    'max': '100',
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields['player'].queryset = (
            Player.objects
            .filter(is_active=True)
            .select_related('team', 'age_group')
            .order_by(
                'name',
                'second_name',
                'surname'
            )
        )

        self.fields['player'].label = "Player"

        self.fields['age_group'].label = "Age Group"
        self.fields['team'].label = "Team"

    def clean(self):

        cleaned_data = super().clean()

        age_group = cleaned_data.get('age_group')
        team = cleaned_data.get('team')
        player = cleaned_data.get('player')

        if player:

            if age_group and player.age_group != age_group:
                self.add_error(
                    'player',
                    'The selected player does not belong to the selected age group.'
                )

            if team and player.team != team:
                self.add_error(
                    'player',
                    'The selected player does not belong to the selected team.'
                )

        return cleaned_data