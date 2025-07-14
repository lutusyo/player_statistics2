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

    # Goalkeeping-specific fields
    is_goalkeeper = models.BooleanField(default=False)
    saves_success_rate = models.FloatField(default=0.0, blank=True)
    clean_sheets = models.PositiveIntegerField(default=0, blank=True)
    catches = models.PositiveIntegerField(default=0, blank=True)
    punches = models.PositiveIntegerField(default=0, blank=True)
    drops = models.PositiveIntegerField(default=0, blank=True)
    penalties_saved = models.PositiveIntegerField(default=0, blank=True)
    clearances = models.PositiveIntegerField(default=0, blank=True)

    # Distribution
    total_passes = models.PositiveIntegerField(default=0, blank=True)
    pass_success_rate = models.FloatField(default=0.0, blank=True)
    long_pass_success = models.FloatField(default=0.0, blank=True)

    # Discipline
    fouls_won = models.PositiveIntegerField(default=0, blank=True)
    fouls_conceded = models.PositiveIntegerField(default=0, blank=True)
    yellow_cards = models.PositiveIntegerField(default=0, blank=True)
    red_cards = models.PositiveIntegerField(default=0, blank=True)

    class Meta:
        unique_together = ('player', 'match')

    def __str__(self):
        return f"{self.player.name} - {self.match}"

    @property
    def goals(self):
        return Goal.objects.filter(match=self.match, scorer=self.player, is_own_goal=False).count()

    @property
    def assists(self):
        return Goal.objects.filter(match=self.match, assist_by=self.player).count()

