# reports_app/models/before_action_review.py

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from version1.teams_app.models import Team
from version1.reports_app.models.weekly_report import WeeklyReport



# Number 7
class DecisionPoint(models.Model):
    report = models.ForeignKey(WeeklyReport,on_delete=models.CASCADE,related_name="decision_points")
    decision = models.TextField()
    responsible = models.CharField(max_length=150,blank=True)
    deadline = models.DateField(null=True,blank=True)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True,blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["completed", "deadline"]

    def __str__(self):
        return self.decision[:100]