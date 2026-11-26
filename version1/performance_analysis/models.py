
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Q

from version1.teams_app.models import (
    Team,
    AgeGroup,
    TeamSquadPhoto,
)


class Analysis(models.Model):

    class AnalysisType(models.TextChoices):
        MATCH = "MATCH", "Match Analysis"
        PLAYER = "PLAYER", "Player Analysis"
        TRAINING = "TRAINING", "Training Analysis"
        TECHNICAL = "TECHNICAL", "Technical Analysis"
        COMPREHENSIVE = "COMPREHENSIVE", "Comprehensive Analysis"

    class ComparisonMode(models.TextChoices):
        SAME_TEAMS = "SAME_TEAMS", "Same Teams Across Periods"
        PER_PERIOD = "PER_PERIOD", "Different Teams Per Period"

    name = models.CharField(max_length=200)

    description = models.TextField(blank=True)

    analysis_type = models.CharField(
        max_length=20,
        choices=AnalysisType.choices,
        default=AnalysisType.MATCH
    )

    comparison_mode = models.CharField(
        max_length=20,
        choices=ComparisonMode.choices,
        default=ComparisonMode.SAME_TEAMS
    )

    age_groups = models.ManyToManyField(
        AgeGroup,
        blank=True,
        related_name="performance_analyses"
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="performance_analyses"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class AnalysisPeriod(models.Model):

    analysis = models.ForeignKey(
        Analysis,
        on_delete=models.CASCADE,
        related_name="periods"
    )

    name = models.CharField(
        max_length=100,
        help_text="Example: Period 1, Pre-season, Phase 1"
    )

    start_date = models.DateField()
    end_date = models.DateField()

    order = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ["order", "start_date"]

        constraints = [
            models.UniqueConstraint(
                fields=["analysis", "order"],
                name="unique_analysis_period_order"
            )
        ]

    def clean(self):
        if self.end_date and self.start_date:
            if self.end_date < self.start_date:
                raise ValidationError({
                    "end_date": "End date cannot be before start date."
                })

    def __str__(self):
        return f"{self.analysis.name} - {self.name}"


class AnalysisTeam(models.Model):
    """
    Teams selected once for the entire analysis.
    Used when comparison_mode = SAME_TEAMS.
    """

    analysis = models.ForeignKey(
        Analysis,
        on_delete=models.CASCADE,
        related_name="selected_teams"
    )

    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="analysis_selections"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["analysis", "team"],
                name="unique_analysis_team"
            )
        ]

    def clean(self):
        if self.team_id and self.team.team_type != "OUR_TEAM":
            raise ValidationError(
                "Only academy teams can be selected."
            )

        if (
            self.analysis_id
            and self.analysis.comparison_mode != Analysis.ComparisonMode.SAME_TEAMS
        ):
            raise ValidationError(
                "Use period-specific team selections for this comparison mode."
            )

    def __str__(self):
        return f"{self.analysis.name} - {self.team.name}"


class AnalysisPeriodTeam(models.Model):
    """
    Teams selected separately for individual periods.
    Used when comparison_mode = PER_PERIOD.
    """

    period = models.ForeignKey(
        AnalysisPeriod,
        on_delete=models.CASCADE,
        related_name="selected_teams"
    )

    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="period_analysis_selections"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["period", "team"],
                name="unique_period_team"
            )
        ]

    def clean(self):
        if self.team_id and self.team.team_type != "OUR_TEAM":
            raise ValidationError(
                "Only academy teams can be selected."
            )

        if (
            self.period_id
            and self.period.analysis.comparison_mode
            != Analysis.ComparisonMode.PER_PERIOD
        ):
            raise ValidationError(
                "Use analysis-wide team selections for this comparison mode."
            )

    def __str__(self):
        return f"{self.period.name} - {self.team.name}"






class AnalysisPeriodSquadPhoto(models.Model):
    """
    Stores the squad photo selected for a team
    within a specific analysis period.
    """

    period = models.ForeignKey(
        AnalysisPeriod,
        on_delete=models.CASCADE,
        related_name="squad_photo_selections",
    )

    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="analysis_squad_photo_selections",
    )

    squad_photo = models.ForeignKey(
        TeamSquadPhoto,
        on_delete=models.PROTECT,
        related_name="analysis_selections",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["period", "team"],
                name="unique_period_team_squad_photo",
            )
        ]

    def clean(self):
        if not self.period_id or not self.team_id:
            return

        analysis = self.period.analysis

        if analysis.comparison_mode == Analysis.ComparisonMode.SAME_TEAMS:
            team_selected = analysis.selected_teams.filter(
                team_id=self.team_id
            ).exists()

        else:
            team_selected = self.period.selected_teams.filter(
                team_id=self.team_id
            ).exists()

        if not team_selected:
            raise ValidationError(
                "This team is not selected for this analysis period."
            )

        if (
            self.squad_photo_id
            and self.squad_photo.team_id != self.team_id
        ):
            raise ValidationError(
                "The selected squad photo does not belong to this team."
            )

    def __str__(self):
        return f"{self.period.name} - {self.team} - Squad Photo"





class AnalysisRun(models.Model):

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        COMPLETED = "COMPLETED", "Completed"
        FAILED = "FAILED", "Failed"

    analysis = models.ForeignKey(
        Analysis,
        on_delete=models.CASCADE,
        related_name="runs"
    )

    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    generated_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    filters_snapshot = models.JSONField(default=dict, blank=True)

    results_snapshot = models.JSONField(default=dict, blank=True)

    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ["-generated_at"]

    def __str__(self):
        return f"{self.analysis.name} - {self.generated_at:%Y-%m-%d %H:%M}"
