# matches_app/models.py
from django.db import models
from players_app.models import Player
from teams_app.models import Team, AgeGroup
from django.utils import timezone


### CHOICES ###

class SeasonChoices(models.TextChoices):
    SEASON_2022_2023 = "2022/2023", "2022/2023"
    SEASON_2023_2024 = "2023/2024", "2023/2024"
    SEASON_2024_2025 = "2024/2025", "2024/2025"
    SEASON_2025_2026 = "2025/2026", "2025/2026"

class CompetitionType(models.TextChoices):
    LOCAL_FRIENDLY = 'Local Friendly', 'Local Friendly'
    INTERNATIONAL_FRIENDLY = 'International Friendly', 'International Friendly'
    NBC_YOUTH_LEAGUE = 'NBC Youth League', 'NBC Youth League'

class VenueChoices(models.TextChoices):
    CHAMAZI_COMPLEX = 'AZAM COMPLEX', 'AZAM COMPLEX'


class Match(models.Model):
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home_matches')
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away_matches')
    date = models.DateField()
    time = models.TimeField(null=True, blank=True)
    venue = models.CharField(max_length=50, choices=VenueChoices.choices,default=VenueChoices.CHAMAZI_COMPLEX)
    season = models.CharField(max_length=20, choices=SeasonChoices.choices)
    competition_type = models.CharField(max_length=50, choices=CompetitionType.choices)
    age_group = models.ForeignKey(AgeGroup, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.home_team.name} vs {self.away_team.name} ({self.date})"
    
# We reference other apps using the app-label.model-name string to avoid circular imports




