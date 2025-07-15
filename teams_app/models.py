# teams_app/models.py
from django.db import models
from players_app.models import AGE_GROUP_CHOICES

class staffMember(models.Model):
    ROLE_CHOICES = [
        ('HEAD_COACH', 'Head Coach'),
        ('ASSISTANT_COACH', 'Assistant Coach'),
        ('GOALKEEPER_COACH', 'Goalkeeper Coach'),
        ('FITNESS_COACH', 'Fitness Coach'),
        ('PHYSIO', 'Physiotherapist'),
        ('ANALYST', 'Performance Analyst'),
        ('TEAM_MANAGER', 'Team Manager'),
        ('PSYCHOLOGIST','Psychologist'),
        ('MEDIA_TEAM', 'Media Team'),
        ('OTHER', 'Other'),
    ]

    name = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    age_group = models.CharField(max_length=20, choices=AGE_GROUP_CHOICES)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    photo = models.ImageField(upload_to='staff_photos/', blank=True, null=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} - {self.get_role_display()} ({self.age_group})"
