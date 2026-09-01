from django import forms
from apps.gym_data.models import (
    GymSession,
    GymGroup,
    GroupExercise,
    GymType,
    Exercise,
    ExerciseCategory,
)


class GymSessionForm(forms.ModelForm):

    class Meta:
        model = GymSession
        fields = ["date", "team"]

        widgets = {
            "date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                }
            ),
            "team": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
        }


class GymGroupForm(forms.ModelForm):

    class Meta:
        model = GymGroup
        fields = ["gym_type", "players"]

        widgets = {
            "gym_type": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "players": forms.SelectMultiple(
                attrs={
                    "class": "form-select player-select",
                }
            ),
        }


class GroupExerciseForm(forms.ModelForm):

    class Meta:
        model = GroupExercise
        fields = [
            "exercise",
            "weight_kg",
            "sets",
            "reps",
        ]

        widgets = {
            "exercise": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "weight_kg": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                }
            ),
            "sets": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1",
                }
            ),
            "reps": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1",
                }
            ),
        }


class GymReportFilterForm(forms.Form):

    team = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label="All Teams",
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )

    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "form-control",
            }
        ),
    )

    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "form-control",
            }
        ),
    )

    category = forms.ModelChoiceField(
        queryset=ExerciseCategory.objects.all(),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )

    exercise = forms.ModelChoiceField(
        queryset=Exercise.objects.all(),
        required=False,
        empty_label="All Exercises",
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        from version1.teams_app.models import Team

        self.fields["team"].queryset = Team.objects.all()