from django import forms
from apps.medical_data.models.medical_visit import MedicalVisit

from apps.core.choices import (
    VisitType,
    MainComplaint,
    AvailabilityStatus,
)


class MedicalFilterForm(forms.Form):

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

    player = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label="All Players",
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )

    visit_type = forms.ChoiceField(
        required=False,
        choices=[
            ("", "All Visit Types"),
            *VisitType.choices,
        ],
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )

    main_complaint = forms.ChoiceField(
        required=False,
        choices=[
            ("", "All Complaints"),
            *MainComplaint.choices,
        ],
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )

    availability_status = forms.ChoiceField(
        required=False,
        choices=[
            ("", "All Availability"),
            *AvailabilityStatus.choices,
        ],
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        from version1.teams_app.models import Team
        from version1.players_app.models import Player

        self.fields["team"].queryset = Team.objects.all()

        self.fields["player"].queryset = Player.objects.all()