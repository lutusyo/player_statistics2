from django.db import models
from players_app.models import Player

class AgeGroup(models.TextChoices):
    UNDER_20 = 'U20', 'Under 20'
    UNDER_17 = 'U17', 'Under 17'
    UNDER_15 = 'U15', 'Under 15'
    UNDER_13 = 'U13', 'Under 13'


class SeasonChoices(models.TextChoices):
    SEASON_2022_2023 = "2022/2023", "2022/2023"
    SEASON_2023_2024 = "2023/2024", "2023/2024"
    SEASON_2024_2025 = "2024/2025", "2024/2025"
    SEASON_2025_2026 = "2025/2026", "2025/2026"


class CompetitionType(models.TextChoices):
    LOCAL_FRIENDLY = 'Local Friendly', 'Local Friendly'
    INTERNATIONAL_FRIENDLY = 'International Friendly', 'International Friendly'
    NBC_YOUTH_LEAGUE = 'NBC Youth League', 'NBC Youth League'

class FormationChoices(models.TextChoices):
    FOUR_THREE_THREE = "4-3-3", "4-3-3"
    FOUR_TWO_THREE_ONE = "4-2-3-1", "4-2-3-1"
    FOUR_FOUR_TWO = "4-4-2", "4-4-2"
    THREE_FIVE_TWO = "3-5-2", "3-5-2"
    THREE_FOUR_THREE = "3-4-3", "3-4-3"

FORMATION_POSITIONS = {
    "4-3-3": ["GK", "RB", "CB1", "CB2", "LB", "CM1", "CDM", "CM2", "RW", "ST", "LW"],
    "4-2-3-1": ["GK", "RB", "CB1", "CB2", "LB", "CDM1", "CDM2", "RW", "CAM", "LW", "ST"],
    "4-4-2": ["GK", "RB", "CB1", "CB2", "LB", "RM", "CM1", "CM2", "LM", "ST1", "ST2"],
    "3-5-2": ["GK", "CB1", "CB2", "CB3", "LWB", "CM1", "CDM", "CM2", "RWB", "ST1", "ST2"],
    "3-4-3": ["GK", "CB1", "CB2", "CB3", "LWB", "CM1", "CM2", "RWB", "LW", "ST", "RW"],
}

class PlayerPosition(models.TextChoices):
    GK = 'GK', 'Goalkeeper'
    RB = 'RB', 'Right Back'
    LB = 'LB', 'Left Back'
    CB1 = 'CB1', 'Center Back 1'
    CB2 = 'CB2', 'Center Back 2'
    CB3 = 'CB3', 'Center Back 3'
    RWB = 'RWB', 'Right Wing Back'
    LWB = 'LWB', 'Left Wing Back'
    CM1 = 'CM1', 'Center Midfield 1'
    CM2 = 'CM2', 'Center Midfield 2'
    CDM = 'CDM', 'Defensive Midfield'
    CAM = 'CAM', 'Attacking Midfield'
    RM = 'RM', 'Right Midfield'
    LM = 'LM', 'Left Midfield'
    RW = 'RW', 'Right Wing'
    LW = 'LW', 'Left Wing'
    ST = 'ST', 'Striker'
    ST1 = 'ST1', 'Striker 1'
    ST2 = 'ST2', 'Striker 2'



class Match(models.Model):
    team = models.CharField(max_length=10, choices=AgeGroup.choices, default=AgeGroup.UNDER_20)

    formation = models.CharField(
        max_length=20,
        choices=FormationChoices.choices,
        blank=True,
        null=True
    )


    date = models.DateField()
    match_time = models.TimeField(null=True, blank=True)
    opponent = models.CharField(max_length=100)
    is_home = models.BooleanField(default=True)
    venue = models.CharField(max_length=100, default='Azam Complex')
    season = models.CharField(max_length=20, choices=SeasonChoices.choices)
    competition_type = models.CharField(max_length=50, choices=CompetitionType.choices, default=CompetitionType.LOCAL_FRIENDLY)
    our_team_logo = models.ImageField(upload_to='team_logo', null=True, blank=True)
    opponent_logo = models.ImageField(upload_to='team_logo/', null=True, blank=True)

    def __str__(self):
        return f"{self.get_team_display()} vs {self.opponent} on {self.date}"
    

class Goal(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='goals')
    scorer = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, related_name='goals_scored')
    assist_by = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, related_name='assists_made')
    minute = models.PositiveIntegerField()
    is_own_goal = models.BooleanField(default=False)

    def __str__(self):
        if self.is_own_goal:
            return f"Own Goal at {self.minute}'"
        return f"{self.scorer} scored at {self.minute}'"
    
class TeamMatchResult(models.Model):
    match = models.OneToOneField(Match, on_delete=models.CASCADE)
    our_score = models.PositiveIntegerField()
    opponent_score = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.our_score} - {self.opponent_score}"
    
class PlayerMatchStats(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)

    minutes_played = models.PositiveIntegerField(default=0)
    is_starting = models.BooleanField(default=False)
    position = models.CharField(
        max_length=10,
        choices=PlayerPosition.choices,
        blank=True,
        null=True,
        help_text="Position in formation (used for pitch layout)"
    )


    class Meta:
        unique_together = ('player', 'match')

    def __str__(self):
        return f"{self.player.name} - {self.get_position_display() or 'No Position'} - {'Starting' if self.is_starting else 'Sub'}  - {self.match}"

    @property
    def position_code(self):
        return self.position



