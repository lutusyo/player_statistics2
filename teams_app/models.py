# teams_app/models.py
from django.db import models


class AgeGroup(models.Model):
    code = models.CharField(max_length=10, unique=True)  # e.g., U20
    name = models.CharField(max_length=50)  # e.g., Under 20

    def __str__(self):
        return self.name

class Team(models.Model): 
    TEAM_TYPE_CHOICES = [
        ('OUR_TEAM', 'Our Team'),
        ('OPPONENT', 'Opponent Team'),
    ]

    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=50, blank=True)
    age_group = models.ForeignKey(AgeGroup, on_delete=models.SET_NULL, null=True, blank=True)
    team_type = models.CharField(max_length=20, choices=TEAM_TYPE_CHOICES, default='OUR_TEAM')
    logo = models.ImageField(upload_to='team_logos/', blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'age_group'], name='unique_team_per_age_group')
        ]

    def __str__(self):
        if self.age_group:
            return f"{self.name} ({self.age_group.name})"
        return self.name


class StaffMember(models.Model):
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
    age_group = models.ForeignKey(AgeGroup, on_delete=models.SET_NULL, null=True, blank=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    photo = models.ImageField(upload_to='staff_photos/', blank=True, null=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} - {self.get_role_display()} ({self.age_group})"
