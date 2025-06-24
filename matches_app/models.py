from django.db import models
from players_app.models import Player

class AgeGroup(models.TextChoices):
    UNDER_20 = 'U20', 'Under 20'
    UNDER_17 = 'U17', 'Under 17'
    UNDER_15 = 'U15', 'Under 15'


class SeasonChoices(models.TextChoices):
    SEASON_2022_2023 = "2022/2023", "2022/2023"
    SEASON_2023_2024 = "2023/2024", "2023/2024"
    SEASON_2024_2025 = "2024/2025", "2024/2025"


class CompetitionType(models.TextChoices):
    LOCAL_FRIENDLY = 'Local Friendly', 'Local Friendly'
    INTERNATIONAL_FRIENDLY = 'International Friendly', 'International Friendly'
    NBC_YOUTH_LEAGUE = 'NBC Youth League', 'NBC Youth League'


class Match(models.Model):
    team = models.CharField(max_length=10, choices=AgeGroup.choices, default=AgeGroup.UNDER_20)

    date = models.DateField()
    match_time = models.TimeField(null=True, blank=True)
    opponent = models.CharField(max_length=100)
    is_home = models.BooleanField(default=True)
    venue = models.CharField(max_length=100, default='Azam Complex')
    season = models.CharField(max_length=20, choices=SeasonChoices.choices)
    competition_type = models.CharField(max_length=50, choices=CompetitionType.choices, default=CompetitionType.LOCAL_FRIENDLY)

    def __str__(self):
        return f"{self.get_team_display()} vs {self.opponent} on {self.date}"
    


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
