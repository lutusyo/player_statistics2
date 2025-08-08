# matches_app/models.py
from django.db import models
from players_app.models import Player
from teams_app.models import Team, AgeGroup

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
    CHAMAZI_COMPLEX = 'CHAMAZI COMPLEX', 'CHAMAZI COMPLEX'

class PositionChoices(models.TextChoices):
    GK = 'GK', 'Goalkeeper'
    LB = 'LB', 'Left Back'
    CB = 'CB', 'Center Back'
    RB = 'RB', 'Right Back'
    DM = 'DM', 'Defensive Midfielder'
    CM = 'CM', 'Central Midfielder'
    AM = 'AM', 'Attacking Midfielder'
    LW = 'LW', 'Left Winger'
    RW = 'RW', 'Right Winger'
    ST = 'ST', 'Striker'
    SUB = 'SUB', 'Substitute'

### CORE MODELS ###

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
class MatchLineup(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, null=True, blank=True)
    player = models.ForeignKey(Player, on_delete=models.CASCADE, null=True, blank=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True)

    is_starting = models.BooleanField(default=False)
    position = models.CharField(
        max_length=5,
        choices=PositionChoices.choices,
        default=PositionChoices.SUB,
        blank=True,
        null=True
    )
    pod_number = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text="GPS Pod number assigned to the player in this match"
    )
    time_entered = models.TimeField(
        null=True,
        blank=True,
        help_text="Time the player entered the field (for subs)"
    )

    class Meta:
        unique_together = ('match', 'player', 'pod_number')

    def __str__(self):
        return f"{self.player.name if self.player else 'No Player'} - {self.get_position_display() if self.position else 'No Position'} - {self.pod_number or 'No Pod'} - ({'Start' if self.is_starting else 'Sub'})"

class Substitution(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    player_out = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='subs_out')
    player_in = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='subs_in')
    minute = models.PositiveIntegerField()
    second = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.player_out} ⬇ → {self.player_in} ⬆ @ {self.minute}:{self.second:02d}"


