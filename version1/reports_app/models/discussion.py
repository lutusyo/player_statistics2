#reports_app/models/discusion.py
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from version1.teams_app.models import Team
from version1.reports_app.models.weekly_report import WeeklyReport


class DiscussionPoint(models.Model):

    class Category(models.TextChoices):
        TECHNICAL = "TECHNICAL", "Technical"
        TACTICAL = "TACTICAL", "Tactical"
        PHYSICAL = "PHYSICAL", "Physical"
        MEDICAL = "MEDICAL", "Medical"
        PLAYER = "PLAYER", "Player"
        ADMINISTRATIVE = "ADMIN", "Administrative"
        OTHER = "OTHER", "Other"

    report = models.ForeignKey(WeeklyReport,on_delete=models.CASCADE,related_name="discussion_points")
    category = models.CharField(max_length=20,choices=Category.choices,default=Category.OTHER)
    point = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.point[:80]