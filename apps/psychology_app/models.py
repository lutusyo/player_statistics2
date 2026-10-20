from django.db import models
from version1.players_app.models import Player

class Assessment(models.Model):

    TASK_CHOICES = [
        ('Insertion', 'Insertion'),
        ('Observation', 'Observation'),
    ]

    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='psychology_app_assessments',)

    start_date = models.DateField()
    end_date = models.DateField()

    task = models.CharField(max_length=20, choices=TASK_CHOICES,)
    iq_range = models.PositiveSmallIntegerField(null=True, blank=True,)
    cognitive_percent = models.FloatField(null=True,blank=True,)
    personality_percent = models.FloatField(null=True, blank=True,)
    neuro_psychology_percent = models.FloatField(null=True,blank=True,)
    education_percent = models.FloatField(null=True, blank=True,)
    overall = models.FloatField(null=True, blank=True,editable=False,)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        scores = [
            self.cognitive_percent,
            self.personality_percent,
            self.neuro_psychology_percent,
            self.education_percent,
        ]

        valid_scores = [
            score for score in scores
            if score is not None
        ]

        self.overall = (
            round(sum(valid_scores) / len(valid_scores), 2)
            if valid_scores else None
        )

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.player.full_name} - {self.task}"

    class Meta:
        ordering = ['-start_date']
