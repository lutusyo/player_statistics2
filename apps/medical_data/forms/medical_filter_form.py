from django import forms
from version1.teams_app.models import Team
from version1.players_app.models import Player
from apps.core.choices import (VisitType, MainComplaint, AvailabilityStatus,)


class MedicalFilterForm(forms.Form):

    start_date = forms.DateField(required=False,
        widget=forms.DateInput(
            attrs={"type": "date", "class": "form-control",}
        ),
    )

    end_date = forms.DateField(required=False,
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "form-control",
            }
        ),
    )

    team = forms.ModelChoiceField(
        queryset=Team.objects.all().order_by("name"),
        required=False,
        empty_label="All Teams",
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )

    player = forms.ModelChoiceField(
        queryset=Player.objects.all().order_by(
            "name",
            "surname",
        ),
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
        choices=[("", "All")] + list(VisitType.choices),
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )

    main_complaint = forms.ChoiceField(
        required=False,
        choices=[("", "All")] + list(MainComplaint.choices),
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )

    availability_status = forms.ChoiceField(
        required=False,
        choices=[("", "All")] + list(AvailabilityStatus.choices),
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )