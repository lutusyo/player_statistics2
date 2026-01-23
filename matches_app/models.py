from django.db import models
from players_app.models import Player
from teams_app.models import Team, AgeGroup
from django.utils import timezone
from datetime import datetime, timedelta

# -------------------------------
# Choices
# -------------------------------
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
    AZAM_INTERNATIONAL_TALENT_SHOWCASE = 'Azam International Talent Showcase', 'Azam International Talent Showcase'
    NMB_MAPINDUZI_CUP = 'NMB Mapinduzi Cup', 'NMB Mapinduzi Cup'
    TOURNAMENT = 'Tournament', 'Tournament'


# -------------------------------
# Countries, Regions & Venues
# -------------------------------
class Country(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Region(models.Model):
    name = models.CharField(max_length=50)
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, related_name="regions", null=True, blank=True
    )

    class Meta:
        unique_together = ("name", "country")

    def __str__(self):
        if self.country:
            return f"{self.name} ({self.country.name})"
        return self.name


class Venue(models.Model):
    name = models.CharField(max_length=100, unique=True)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='venues')

    def __str__(self):
        return f"{self.name} ({self.region.name})"


# -------------------------------
# Competition (to hold logo per type)
# -------------------------------
class Competition(models.Model):
    name = models.CharField(max_length=100, unique=True)
    type = models.CharField(max_length=50, choices=CompetitionType.choices)
    logo = models.ImageField(upload_to='competition_logos/', null=True, blank=True)

    def __str__(self):
        return self.name


# -------------------------------
# Matches
# -------------------------------
class Match(models.Model):
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home_matches')
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away_matches')
    date = models.DateField()
    time = models.TimeField(null=True, blank=True)  # kickoff time
    venue = models.ForeignKey(Venue, on_delete=models.SET_NULL, null=True, blank=True)
    season = models.CharField(max_length=20, choices=SeasonChoices.choices)
    competition = models.ForeignKey(Competition, on_delete=models.SET_NULL, null=True, blank=True)
    age_group = models.ForeignKey(AgeGroup, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Optional group/phase (e.g., Group A, Quarterfinals)
    group = models.CharField(max_length=50, blank=True, null=True, help_text="Optional group/phase for competition")

    opponent_yellow_cards = models.PositiveIntegerField(default=0)
    opponent_red_cards = models.PositiveIntegerField(default=0)
    rating_links_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.home_team.name} vs {self.away_team.name} ({self.date})"

    @property
    def start_time(self):
        """Return kickoff as timezone-aware datetime."""
        if self.time:
            dt = datetime.combine(self.date, self.time)  # naive
            return timezone.make_aware(dt)  # make it aware using Django settings
        return None

    @property
    def end_time(self):
        """Return match end time (90 mins after start)."""
        if self.start_time:
            return self.start_time + timedelta(minutes=90)
        return None

    def elapsed_minutes(self):
        """Return how many minutes have passed since kickoff."""
        if not self.start_time:
            return 0
        now = timezone.now()
        if now > self.end_time:
            return 90
        return int((now - self.start_time).total_seconds() // 60)

    def status(self):
        """Return match status string."""
        if not self.start_time:
            return "not_started"
        now = timezone.now()
        if now >= self.end_time:
            return "ended"
        return "running"
