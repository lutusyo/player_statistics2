# reports_app/models/before_action_review.py

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from version1.teams_app.models import Team
from version1.reports_app.models.weekly_report import WeeklyReport


class BeforeActionReview(models.Model):

    report = models.OneToOneField(WeeklyReport,on_delete=models.CASCADE,related_name="before_action_review")
    previous_week_review = models.TextField(blank=True)
    objectives = models.TextField(blank=True)
    planned_activities = models.TextField(blank=True)
    expected_challenges = models.TextField(blank=True)
    targeted_interventions = models.TextField(blank=True)
    expected_outcomes = models.TextField(blank=True)
    coach_comments = models.TextField(blank=True)

    def __str__(self):
        return (
            f"BAR - {self.report.team} "
            f"Week {self.report.week}"
        )