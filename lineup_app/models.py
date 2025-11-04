# lineup_app/models.py
from django.db import models
from players_app.models import Player
from matches_app.models import Match
from teams_app.models import Team



# Map position codes to pitch coordinates (% from top, % from left)
POSITION_COORDS = {
    "4-4-2": {
        "GK": {"top": 5, "left": 45},
        "LB": {"top": 25, "left": 20},
        "LCB": {"top": 25, "left": 40},
        "RCB": {"top": 25, "left": 60},
        "RB": {"top": 25, "left": 80},
        "LM": {"top": 50, "left": 35},
        "LCM": {"top": 50, "left": 45},
        "RCM": {"top": 50, "left": 55},
        "RM": {"top": 50, "left": 65},
        "ST1": {"top": 75, "left": 40},
        "ST2": {"top": 75, "left": 60},
    },
    "4-3-3": {
        "GK": {"top": 5, "left": 45},
        "LB": {"top": 25, "left": 20},
        "LCB": {"top": 25, "left": 40},
        "RCB": {"top": 25, "left": 60},
        "RB": {"top": 25, "left": 80},
        "LCM": {"top": 50, "left": 35},
        "CM": {"top": 50, "left": 50},
        "RCM": {"top": 50, "left": 65},
        "LW": {"top": 70, "left": 25},
        "ST": {"top": 75, "left": 50},
        "RW": {"top": 70, "left": 75},
    },
    "3-5-2": {
        "GK": {"top": 5, "left": 45},
        "LCB": {"top": 25, "left": 35},
        "CB": {"top": 25, "left": 50},
        "RCB": {"top": 25, "left": 65},
        "LM": {"top": 45, "left": 20},
        "LCM": {"top": 45, "left": 40},
        "CM": {"top": 50, "left": 50},
        "RCM": {"top": 45, "left": 60},
        "RM": {"top": 45, "left": 80},
        "ST1": {"top": 70, "left": 40},
        "ST2": {"top": 70, "left": 60},
    },
    "3-4-3": {
        "GK": {"top": 5, "left": 45},
        "LCB": {"top": 25, "left": 30},
        "CB": {"top": 25, "left": 50},
        "RCB": {"top": 25, "left": 70},
        "LM": {"top": 45, "left": 35},
        "LCM": {"top": 45, "left": 45},
        "RCM": {"top": 45, "left": 55},
        "RM": {"top": 45, "left": 65},
        "LW": {"top": 70, "left": 25},
        "ST": {"top": 70, "left": 50},
        "RW": {"top": 70, "left": 75},
    },
    "4-5-1": {
        "GK": {"top": 5, "left": 45},
        "LB": {"top": 25, "left": 20},
        "LCB": {"top": 25, "left": 40},
        "RCB": {"top": 25, "left": 60},
        "RB": {"top": 25, "left": 80},
        "LM": {"top": 45, "left": 25},
        "LCM": {"top": 45, "left": 40},
        "CM": {"top": 50, "left": 50},
        "RCM": {"top": 45, "left": 60},
        "RM": {"top": 45, "left": 75},
        "ST": {"top": 70, "left": 50},
    },

    
    #"4-2-3-1":{
     #   "GK": {"top": 5, "left": 45},
      #  "LB": {"top": 25, "left": 20},
      #  "LCB": {"top": 25, "left": 40},
       # "RCB": {"top": 25, "left": 60},
       # "RB": {"top": 25, "left": 80},
      #  "LM": {"top": 45, "left": 25},
      #  "LCM": {"top": 45, "left": 40},
      #  "CM": {"top": 50, "left": 50},
      #  "RCM": {"top": 45, "left": 60},
       # "RM": {"top": 45, "left": 75},
       # "ST": {"top": 70, "left": 50},
   # },
}


class Formation(models.TextChoices):
    F442 = "4-4-2", "4-4-2"
    F433 = "4-3-3", "4-3-3"
    F352 = "3-5-2", "3-5-2"
    F343 = "3-4-3", "3-4-3"
    F451 = "4-5-1", "4-5-1"
    #F4231 = "4-2-3-1", "4-2-3-1"



class PositionChoices(models.TextChoices):
    GK = 'GK', 'Goalkeeper'
    LB = 'LB', 'Left Back'
    LCB = 'LCB', 'Left Center Back'
    RCB = 'RCB', 'Right Center Back'
    RB = 'RB', 'Right Back'
    LM = 'LM', 'Left Midfielder'
    LCM = 'LCM', 'Left Central Midfielder'
    RCM = 'RCM', 'Right Central Midfielder'
    RM = 'RM', 'Right Midfielder'
    ST1 = 'ST1', 'Striker 1'
    ST2 = 'ST2', 'Striker 2'
    LW = 'LW', 'Left Winger'
    RW = 'RW', 'Right Winger'
    ST = 'ST', 'Striker'
    CM = 'CM', 'Central Midfielder'
    CB = 'CB', 'Center Back'
    SUB = 'SUB', 'Substitute'






class MatchLineup(models.Model):
    formation = models.CharField(max_length=10, choices=Formation.choices, blank=True, null=True)
    match = models.ForeignKey(Match, on_delete=models.CASCADE, null=True, blank=True)
    player = models.ForeignKey(Player, on_delete=models.CASCADE, null=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True)
    is_starting = models.BooleanField(default=False)
    position = models.CharField(max_length=5, choices=PositionChoices.choices, default=PositionChoices.SUB, blank=True, null=True)
    pod_number = models.CharField(max_length=20, null=True, blank=True)
    time_in = models.PositiveSmallIntegerField(null=True, blank=True)
    time_out = models.PositiveSmallIntegerField(null=True, blank=True)
    minutes_played = models.PositiveSmallIntegerField(default=0)
    order = models.PositiveSmallIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['match', 'team', 'player'], name='unique_lineup_per_team'),
        ]
        ordering = ['order', 'player__name']

    def __str__(self):
        return f"{self.match} - {self.team} - {self.player}"

    def calculate_minutes_played(self, final_minute=None):
        if self.time_in is None:
            return 0

        # Decide exit time
        if self.time_out is not None:
            end_minute = self.time_out
        elif final_minute is not None:
            end_minute = final_minute
        else:
            return 0

        mp = end_minute - self.time_in
        return mp if mp > 0 else 0

    def save(self, *args, **kwargs):
        """
        Override save so minutes_played always updates automatically.
        By default assume 90 minutes match duration if still active.
        """
        self.minutes_played = self.calculate_minutes_played(final_minute=90)
        super().save(*args, **kwargs)


class Substitution(models.Model):
    # A single substitution event: which player went out, which came in, and at what minute
    match = models.ForeignKey(Match, on_delete=models.CASCADE, help_text='Match where substitution happened')
    player_out = models.ForeignKey(MatchLineup, related_name='substituted_out', on_delete=models.CASCADE, help_text='Lineup row for the player who left the pitch')
    player_in = models.ForeignKey(MatchLineup, related_name='substituted_in', on_delete=models.CASCADE, help_text='Lineup row for the player who came on')

    minute = models.PositiveSmallIntegerField(help_text='Minute when the substitution occurred')
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.match} | {self.player_out.player} -> {self.player_in.player} @{self.minute}"