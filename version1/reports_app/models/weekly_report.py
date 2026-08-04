# reports_app/models.py

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from version1.teams_app.models import Team

from apps.core.choices import CompetitionType, SeasonChoices


class WeeklyReport(models.Model):

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        SUBMITTED = "SUBMITTED", "Submitted"
        APPROVED = "APPROVED", "Approved"
        RETURNED = "RETURNED", "Returned for Revision"

    team = models.ForeignKey(Team,on_delete=models.CASCADE,related_name="weekly_reports")
    season = models.CharField( max_length=20, choices=SeasonChoices.choices)
    week = models.PositiveIntegerField()
    coach = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name="weekly_reports_created")
    week_start = models.DateField()
    week_end = models.DateField()

    title = models.CharField(max_length=255,blank=True)
    executive_summary = models.TextField(blank=True)
    status = models.CharField(max_length=20,choices=Status.choices,default=Status.DRAFT)
    submitted_at = models.DateTimeField(null=True,blank=True)
    approved_at = models.DateTimeField( null=True,blank=True)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name="weekly_reports_approved")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField( auto_now=True)

    class Meta:
        ordering = ["-week_start"]

        constraints = [
            models.UniqueConstraint(
                fields=["team", "season", "week"],
                name="unique_weekly_report_per_team_season_week"
            )
        ]

    def clean(self):
        if self.week_start and self.week_end:
            if self.week_end < self.week_start:
                raise ValidationError(
                    "Week end date cannot be before week start date."
                )

    def __str__(self):
        return (
            f"{self.team} | "
            f"{self.season} | "
            f"Week {self.week}"
        )
