# matches_app/models.py
from django.db import models
from players_app.models import Player
from teams_app.models import Team, AgeGroup
from django.utils import timezone


### CHOICES ###

class SeasonChoices(models.TextChoices):
    SEASON_2022_2023 = "2022-2023", "2022-2023"
    SEASON_2023_2024 = "2023-2024", "2023-2024"
    SEASON_2024_2025 = "2024-2025", "2024-2025"
    SEASON_2025_2026 = "2025-2026", "2025-2026"


class CompetitionType(models.TextChoices):
    LOCAL_FRIENDLY = 'Local Friendly', 'Local Friendly'
    INTERNATIONAL_FRIENDLY = 'International Friendly', 'International Friendly'
    NBC_YOUTH_LEAGUE = 'NBC Youth League', 'NBC Youth League'
    NBC_PREMIER_LEAGUE = 'NBC Premier League', 'NBC Premier League'
    CAF_CONFEDERATION_CUP = 'CAF Confederation Cup', 'CAF Confederation Cup'


class VenueChoices(models.TextChoices):
    CHAMAZI_COMPLEX = 'AZAM COMPLEX', 'AZAM COMPLEX'
    NDC_STADIUM = 'NDC STADIUM', 'NDC STADIUM'
    MAJALIWA = 'MAJALIWA', 'MAJALIWA'


class Match(models.Model):
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home_matches')
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away_matches')
    date = models.DateField()
    time = models.TimeField(null=True, blank=True)
    venue = models.CharField(max_length=50, choices=VenueChoices.choices, default=VenueChoices.CHAMAZI_COMPLEX)
    season = models.CharField(max_length=20, choices=SeasonChoices.choices)
    competition_type = models.CharField(max_length=50, choices=CompetitionType.choices)
    age_group = models.ForeignKey(AgeGroup, on_delete=models.SET_NULL, null=True, blank=True)

        # Opponent team cards (for fouls won)
    opponent_yellow_cards = models.PositiveIntegerField(default=0)
    opponent_red_cards = models.PositiveIntegerField(default=0)

    # NEW FIELDS FOR CLOCK
    start_time = models.DateTimeField(null=True, blank=True, help_text="When the match actually started (UTC).")
    end_time = models.DateTimeField(null=True, blank=True, help_text="When the match ended (UTC).")

    def __str__(self):
        return f"{self.home_team.name} vs {self.away_team.name} ({self.date})"

    # ---------- CLOCK HELPERS ----------

    def start_match(self):
        """Set kickoff time (only if not already started)."""
        if not self.start_time:
            self.start_time = timezone.now()
            self.save(update_fields=["start_time"])
        return self.start_time

    def end_match(self):
        """Set final whistle time."""
        if not self.end_time:
            self.end_time = timezone.now()
            self.save(update_fields=["end_time"])
        return self.end_time

    def elapsed_minutes(self):
        """Return how many minutes have passed since kickoff."""
        if not self.start_time:
            return 0
        if self.end_time:
            return int((self.end_time - self.start_time).total_seconds() // 60)
        return int((timezone.now() - self.start_time).total_seconds() // 60)

    def status(self):
        """Return match status string."""
        if not self.start_time:
            return "not_started"
        if self.end_time:
            return "ended"
        return "running"
    
    def has_lineup(self):
        from lineup_app.models import MatchLineup   # import inside to avoid circular import
        return MatchLineup.objects.filter(match=self).exists()
