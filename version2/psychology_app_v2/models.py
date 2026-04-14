from django.db import models


class AgeGroup(models.Model):
    AGE_CHOICES = [
        ('U15', 'U15'),
        ('U17', 'U17'),
        ('U20', 'U20'),
        ('OTHER', 'Other'),
    ]

    name = models.CharField(max_length=10, choices=AGE_CHOICES, unique=True)

    def __str__(self):
        return self.name


class Player(models.Model):
    player_name = models.CharField(max_length=255, unique=True)
    join_date = models.DateField()
    core_character = models.CharField(max_length=50)

    age_group = models.ForeignKey(AgeGroup, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.player_name} ({self.age_group})"


class Assessment(models.Model):
    TASK_CHOICES = [
        ('Insertion', 'Insertion'),
        ('Observation', 'Observation'),
    ]

    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='assessments')

    start_date = models.DateField()
    end_date = models.DateField()
    task = models.CharField(max_length=20, choices=TASK_CHOICES)

    iq_range = models.IntegerField(null=True, blank=True)

    cognitive_percent = models.FloatField(null=True, blank=True)
    personality_percent = models.FloatField(null=True, blank=True)
    neuro_psychology_percent = models.FloatField(null=True, blank=True)
    education_percent = models.FloatField(null=True, blank=True)

    overall = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.player.player_name} - {self.task} ({self.start_date})"