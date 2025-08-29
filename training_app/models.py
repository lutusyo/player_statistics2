from django.db import models
from players_app.models import Player  # Adjust import accordingly

class TrainingSession(models.Model):

    TRAINING_TYPE_CHOICES = [
        ('Fitness', 'Fitness'),
        ('Technical', 'Technical'),
        ('Tactical', 'Tactical'),
        ('Recovery', 'Recovery'),
        ('Match Prep', 'Match Prep'),
    ]

    date = models.DateField(auto_now_add=True)
    duration_minutes = models.PositiveIntegerField()
    # Store training types as comma-separated string
    training_types = models.CharField(max_length=100)  

    def get_training_types_list(self):
        """Return training types as a list"""
        return self.training_types.split(',')

    def __str__(self):
        return f"{self.date} - {self.duration_minutes} mins - {self.training_types}"

class PlayerAttendance(models.Model):
    session = models.ForeignKey(TrainingSession, on_delete=models.CASCADE, related_name='attendances')
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    attended = models.BooleanField(default=False)

    class Meta:
        unique_together = ('session', 'player')

    def __str__(self):
        return f"{self.player.name} - {'Present' if self.attended else 'Absent'}"
