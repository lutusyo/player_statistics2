
from django import forms

from version1.players_app.models import Player
from version1.teams_app.models import AgeGroup, Team, StaffMember

from apps.individual_data.models.data_collection import (
    TrainingTopic,
    TrainingObjective,
    CoachingPoint,
    TrainingSession,
    SessionTopic,
    PlayerParticipation,
    PlayerIntervention,
    SessionEvaluation,
)


class TrainingSessionForm(forms.ModelForm):
    class Meta:
        model = TrainingSession
        fields = [
            "date",
            "age_group",
            "team",
            "coach",
            "training_type",
            "duration_minutes",
            "intensity",
            "notes",
        ]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "age_group": forms.Select(attrs={"class": "form-select"}),
            "team": forms.Select(attrs={"class": "form-select"}),
            "coach": forms.Select(attrs={"class": "form-select"}),
            "training_type": forms.Select(attrs={"class": "form-select"}),
            "duration_minutes": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "intensity": forms.Select(attrs={"class": "form-select"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["age_group"].queryset = AgeGroup.objects.all().order_by("name")
        self.fields["team"].queryset = Team.objects.filter(
            team_type="OUR_TEAM"
        ).order_by("name")
        self.fields["coach"].queryset = StaffMember.objects.all().order_by("name")

        self.fields["team"].required = False
        self.fields["coach"].required = False
        self.fields["duration_minutes"].required = False
        self.fields["intensity"].required = False
        self.fields["notes"].required = False


class SessionTopicForm(forms.ModelForm):
    class Meta:
        model = SessionTopic
        fields = ["topic", "objective"]
        widgets = {
            "topic": forms.Select(attrs={"class": "form-select topic-select"}),
            "objective": forms.Select(attrs={"class": "form-select objective-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["topic"].queryset = TrainingTopic.objects.filter(
            is_active=True
        ).order_by("category", "order", "name")

        self.fields["objective"].queryset = TrainingObjective.objects.none()

        topic_id = (
            self.data.get(self.add_prefix("topic"))
            or getattr(self.instance, "topic_id", None)
        )

        if topic_id:
            self.fields["objective"].queryset = TrainingObjective.objects.filter(
                topic_id=topic_id,
                is_active=True,
            ).order_by("order", "name")


class PlayerParticipationForm(forms.ModelForm):
    class Meta:
        model = PlayerParticipation
        fields = [
            "player",
            "position",
            "participation",
            "minutes",
            "performance",
            "observation",
        ]
        widgets = {
            "player": forms.Select(attrs={"class": "form-select player-select"}),
            "position": forms.Select(attrs={"class": "form-select position-select"}),
            "participation": forms.Select(attrs={"class": "form-select"}),
            "minutes": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "performance": forms.Select(attrs={"class": "form-select"}),
            "observation": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }

    def __init__(self, *args, age_group=None, **kwargs):
        super().__init__(*args, **kwargs)

        players = Player.objects.filter(is_active=True).order_by(
            "surname", "name", "second_name"
        )

        if age_group:
            players = players.filter(age_group=age_group)

        self.fields["player"].queryset = players
        self.fields["observation"].required = False
        self.fields["minutes"].required = False
        self.fields["performance"].required = False
        self.fields["position"].required = False


class PlayerInterventionForm(forms.ModelForm):
    class Meta:
        model = PlayerIntervention
        fields = [
            "session_topic",
            "result",
            "observation",
            "next_action",
        ]
        widgets = {
            "session_topic": forms.Select(attrs={"class": "form-select"}),
            "result": forms.Select(attrs={"class": "form-select"}),
            "observation": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "next_action": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }

    def __init__(self, *args, session=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["session_topic"].queryset = SessionTopic.objects.none()

        if session:
            self.fields["session_topic"].queryset = (
                SessionTopic.objects.filter(session=session)
                .select_related("topic", "objective")
                .order_by("order", "id")
            )

        self.fields["observation"].required = False
        self.fields["next_action"].required = False


class SessionEvaluationForm(forms.ModelForm):
    class Meta:
        model = SessionEvaluation
        fields = [
            "objective_status",
            "training_quality",
            "what_went_well",
            "challenges",
            "coach_comment",
            "next_action",
        ]
        widgets = {
            "objective_status": forms.Select(attrs={"class": "form-select"}),
            "training_quality": forms.Select(attrs={"class": "form-select"}),
            "what_went_well": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "challenges": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "coach_comment": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "next_action": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }
