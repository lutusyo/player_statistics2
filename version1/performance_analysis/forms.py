
from django import forms
from django.forms import formset_factory

from version1.teams_app.models import Team, AgeGroup
from .models import Analysis


ACADEMY_TEAMS = Team.objects.filter(
    team_type="OUR_TEAM"
).select_related("age_group").order_by("age_group__code", "name")


class AnalysisForm(forms.ModelForm):

    age_groups = forms.ModelMultipleChoiceField(
        queryset=AgeGroup.objects.all().order_by("code"),
        widget=forms.SelectMultiple(attrs={
            "class": "form-select",
            "size": 5,
        }),
        required=True,
        label="Age Categories",
    )

    class Meta:
        model = Analysis
        fields = [
            "name",
            "description",
            "analysis_type",
            "comparison_mode",
            "age_groups",
        ]

        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Example: U20 Performance - First Half Season",
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Describe the purpose of this analysis...",
            }),
            "analysis_type": forms.Select(attrs={
                "class": "form-select",
            }),
            "comparison_mode": forms.Select(attrs={
                "class": "form-select",
                "id": "comparisonMode",
            }),
        }


class TeamSelectionForm(forms.Form):

    teams = forms.ModelMultipleChoiceField(
        queryset=ACADEMY_TEAMS,
        required=False,
        widget=forms.SelectMultiple(attrs={
            "class": "form-select",
            "size": 7,
        }),
        label="Select Academy Teams",
    )


class AnalysisPeriodForm(forms.Form):

    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Example: First Six Weeks",
        }),
    )

    start_date = forms.DateField(
        widget=forms.DateInput(attrs={
            "type": "date",
            "class": "form-control",
        }),
    )

    end_date = forms.DateField(
        widget=forms.DateInput(attrs={
            "type": "date",
            "class": "form-control",
        }),
    )

    teams = forms.ModelMultipleChoiceField(
        queryset=ACADEMY_TEAMS,
        required=False,
        widget=forms.SelectMultiple(attrs={
            "class": "form-select",
            "size": 5,
        }),
        label="Teams for this period",
    )

    def clean(self):
        cleaned_data = super().clean()

        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date and end_date < start_date:
            self.add_error(
                "end_date",
                "End date cannot be before start date."
            )

        return cleaned_data


AnalysisPeriodFormSet = formset_factory(
    AnalysisPeriodForm,
    extra=2,
    min_num=2,
    validate_min=True,
    can_delete=True,
)
