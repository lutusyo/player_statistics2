from django.db import models

from version1.reports_app.models.weekly_report import WeeklyReport
from version1.reports_app.models.previous_models import Medical
from apps.core.choices import SeasonChoices
from version1.teams_app.models import Team

class SquadStatus(models.Model):

    report = models.OneToOneField(WeeklyReport,on_delete=models.CASCADE,related_name="squad_status")
    available_players = models.PositiveIntegerField(default=0)
    #injured_players = Medical.objects.filter(team=report.team,status="Injured").count()
    unavailable_players = models.PositiveIntegerField(default=0)
    new_players = models.PositiveIntegerField(default=0)
    summary = models.TextField(blank=True)
    coach_comments = models.TextField(blank=True)

    def __str__(self):
        return (
            f"Squad Status - "
            f"{self.report.team} "
            f"Week {self.report.week}"
        )