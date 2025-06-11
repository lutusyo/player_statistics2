from django.db import models
from players_app.models import Player

UNDER_20 = 'U20'
UNDER_17 = 'U17'
UNDER_15 = 'U15'
AGE_GROUP_CHOICES = [
    (UNDER_20, 'Under 20'),
    (UNDER_17, 'Under 17'),
    (UNDER_15, 'Under 15'),
]

SEASON_CHOICES = [
    ("2022/2023", "2022/2023"),
    ("2023/2024", "2023/2024"),
    ("2024/2025", "2024/2025"),
]

COMPETITION_CHOICES = [
    ('Local Friendly', 'Local Friendly'),
    ('International Friendly', 'International Friendly'),
    ('NBC Youth League', 'NBC Youth League'),
]


class Match(models.Model):
    date = models.DateField()
    opponent = models.CharField(max_length=100)
    is_home = models.BooleanField(default=True)
    season = models.CharField(max_length=20, choices=SEASON_CHOICES)
    competition_type = models.CharField(max_length=50, choices=COMPETITION_CHOICES, default='Local Friendly')

    def __str__(self):
        return f"{self.date} vs {self.opponent}"
    
class PlayerMatchStats(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    goals = models.PositiveIntegerField(default=0)
    assists = models.PositiveIntegerField(default=0)
    minutes_played = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('player', 'match')

    def __str__(self):
        return f"{self.player.name} - {self.match}"