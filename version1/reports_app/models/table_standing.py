
# reports_app/models/table_standing.py

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from version1.teams_app.models import Team
from version1.reports_app.models.weekly_report import WeeklyReport



class TableStanding(models.Model):
    report = models.OneToOneField(WeeklyReport,on_delete=models.CASCADE,related_name="standing")
    standing_image = models.ImageField(upload_to="reports/weekly/standings/")
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.report.team} - Week {self.report.week}"