from django import forms

from version1.teams_app.models import Team
from version1.players_app.models import Player
from apps.medical_data.models import MedicalVisit


class MedicalVisitForm(forms.ModelForm):

    class Meta:

        model = MedicalVisit
        exclude = ("created_by","created_at","updated_at",)
        widgets = {
            "date": forms.DateInput(attrs={"type": "date","class": "form-control",}),
            "team": forms.Select(attrs={"class": "form-select","id": "id_team",}),
            "player": forms.Select(attrs={"class": "form-select","id": "id_player",}),
            "visit_type": forms.Select(attrs={"class": "form-select",}),
            "main_complaint": forms.Select(attrs={"class": "form-select",}),
            "body_side": forms.Select(attrs={"class": "form-select",}),
            "injury_status": forms.Select(attrs={"class": "form-select",}),
            "mechanism_of_injury": forms.Select(attrs={"class": "form-select",}),
            "training_session_status": forms.Select(attrs={"class": "form-select",}),
            "availability_status": forms.Select(attrs={"class": "form-select",}),
            "history_of_injury": forms.Textarea(attrs={"class": "form-control","rows": 3,}),
            "physical_examination": forms.Textarea(attrs={"class": "form-control","rows": 4,}),
            "working_diagnosis": forms.Textarea(attrs={"class": "form-control","rows": 4,}),
            "therapy": forms.Textarea(attrs={"class": "form-control","rows": 4,}),
            "recommendations": forms.Textarea(attrs={"class": "form-control","rows": 4,}),
            "next_review_date": forms.DateInput(attrs={"type": "date","class": "form-control",}),
            "expected_return_date": forms.DateInput(attrs={"type": "date","class": "form-control",}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["team"].queryset = Team.objects.all().order_by("name")
        self.fields["player"].queryset = Player.objects.none()

        if "team" in self.data:
            try:
                team_id = int(self.data.get("team"))
                self.fields["player"].queryset = (
                    Player.objects.filter(team_id=team_id).order_by("name", "second_name", "surname"))

            except (ValueError, TypeError):
                pass

        elif self.instance.pk and self.instance.team_id:
            self.fields["player"].queryset = (
                Player.objects
                .filter(team_id=self.instance.team_id)
                .order_by("name", "second_name", "surname")
            )

    def clean(self):
        cleaned_data = super().clean()
        team = cleaned_data.get("team")
        player = cleaned_data.get("player")

        if player and team:
            if player.team != team:
                raise forms.ValidationError(
                    "Selected player does not belong to the selected team.")

        return cleaned_data