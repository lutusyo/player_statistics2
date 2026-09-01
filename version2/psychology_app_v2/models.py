from django.db import models
from version1.players_app.models import Player


class Assessment(models.Model):

    TASK_CHOICES = [
        ('Insertion', 'Insertion'),
        ('Observation', 'Observation'),
    ]

    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name='psychology_assessments'
    )

    start_date = models.DateField()
    end_date = models.DateField()

    task = models.CharField(
        max_length=20,
        choices=TASK_CHOICES
    )

    iq_range = models.IntegerField(
        null=True,
        blank=True
    )

    cognitive_percent = models.FloatField(
        null=True,
        blank=True
    )

    personality_percent = models.FloatField(
        null=True,
        blank=True
    )

    neuro_psychology_percent = models.FloatField(
        null=True,
        blank=True
    )

    education_percent = models.FloatField(
        null=True,
        blank=True
    )

    overall = models.FloatField(
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.player.full_name} - {self.task} ({self.start_date})"

    class Meta:
        ordering = ['-start_date']