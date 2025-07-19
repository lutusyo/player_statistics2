# announcements_app/models.py
from django.db import models
from django.contrib.auth.models import User
from players_app.models import AGE_GROUP_CHOICES


class Announcement(models.Model):
    date_for = models.DateField()
    age_group = models.CharField(max_length=10, choices=AGE_GROUP_CHOICES)
    title = models.CharField(max_length=100, default='Plan for Tomorrow')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.title} - {self.age_group} - {self.date_for}"
    
class PlanItem(models.Model):
    announcement = models.ForeignKey(Announcement, related_name='plan_items', on_delete=models.CASCADE)
    time = models.TimeField()
    activity = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.time} - {self.activity}"
