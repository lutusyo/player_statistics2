# reports_app/models/after_action_review.py

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from version1.teams_app.models import Team
from version1.reports_app.models.weekly_report import WeeklyReport



class AfterActionReview(models.Model):

    report = models.OneToOneField(WeeklyReport,on_delete=models.CASCADE,related_name="after_action_review")
    planned = models.TextField(blank=True,help_text="What was planned for the week?")
    actual = models.TextField(blank=True,help_text="What actually happened?")
    positives = models.TextField(blank=True)
    negatives = models.TextField(blank=True)
    reasons_for_results = models.TextField(blank=True)
    learning_points = models.TextField(blank=True)
    player_performance_summary = models.TextField(blank=True)
    next_microcycle = models.TextField(blank=True)
    coach_comments = models.TextField(blank=True)

    def __str__(self):
        return (
            f"AAR - {self.report.team} "
            f"Week {self.report.week}"
        )