from django import forms
from version1.players_app.models import Player
from version1.teams_app.models import AgeGroup, Team
from .models import Assessment


class AssessmentForm(forms.ModelForm):

    age_group = forms.ModelChoiceField(
        queryset=AgeGroup.objects.all().order_by('name'),
        required=False,
        empty_label="All Age Groups",
    )

    team = forms.ModelChoiceField(
        queryset=Team.objects.all().order_by('name'),
        required=False,
        empty_label="All Teams",
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
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'iq_range': forms.NumberInput(attrs={'min': 0}),
            'cognitive_percent': forms.NumberInput(
                attrs={'min': 0, 'max': 100, 'step': '0.01'}
            ),
            'personality_percent': forms.NumberInput(
                attrs={'min': 0, 'max': 100, 'step': '0.01'}
            ),
            'neuro_psychology_percent': forms.NumberInput(
                attrs={'min': 0, 'max': 100, 'step': '0.01'}
            ),
            'education_percent': forms.NumberInput(
                attrs={'min': 0, 'max': 100, 'step': '0.01'}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['player'].queryset = (
            Player.objects.filter(is_active=True)
            .select_related('team', 'age_group')
            .order_by('name', 'second_name', 'surname')
        )

    def clean(self):
        cleaned_data = super().clean()

        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        player = cleaned_data.get('player')
        age_group = cleaned_data.get('age_group')
        team = cleaned_data.get('team')

        if start_date and end_date and end_date < start_date:
            self.add_error(
                'end_date',
                'End date cannot be earlier than start date.'
            )

        if player:
            if age_group and player.age_group != age_group:
                self.add_error(
                    'player',
                    'The selected player does not belong to this age group.'
                )

            if team and player.team != team:
                self.add_error(
                    'player',
                    'The selected player does not belong to this team.'
                )

        for field in [
            'cognitive_percent',
            'personality_percent',
            'neuro_psychology_percent',
            'education_percent',
        ]:
            value = cleaned_data.get(field)

            if value is not None and not 0 <= value <= 100:
                self.add_error(field, 'Enter a value between 0 and 100.')

        return cleaned_data