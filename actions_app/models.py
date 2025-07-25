# actions_app/models.py
from django.db import models
from matches_app.models import Match
from players_app.models import Player
  
class TeamActionStats(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name="team_actions_stats")
    team_name = models.CharField(max_length=100, help_text="e.g. AZAM U20 or Opponent", editable=False)
    is_our_team = models.BooleanField(default=True, help_text="Is this for our team? Yes = Our team, No = Opponent")

    shots_on_target_inside_box = models.PositiveIntegerField(default=0)
    shots_on_target_outside_box = models.PositiveIntegerField(default=0)
    shots_off_target_inside_box = models.PositiveIntegerField(default=0)
    shots_off_target_outside_box = models.PositiveIntegerField(default=0)
    blocked_shots = models.PositiveIntegerField(default=0)
    corners = models.PositiveIntegerField(default=0)
    successful_crosses = models.PositiveIntegerField(default=0)
    unsuccessful_crosses = models.PositiveIntegerField(default=0)
    aerial_duel_won = models.PositiveIntegerField(default=0)
    aerial_duel_lost = models.PositiveIntegerField(default=0)
    missed_chances = models.PositiveIntegerField(default=0)
    bad_passes = models.PositiveIntegerField(default=0)
    ball_lost = models.PositiveIntegerField(default=0)
    duel_1v1_won = models.PositiveIntegerField(default=0)
    fouls_committed = models.PositiveIntegerField(default=0)
    fouls_won = models.PositiveIntegerField(default=0)
    mistakes = models.PositiveIntegerField(default=0)
    offsides = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Team Action Stats"
        verbose_name_plural = "Team Action Stats"

    def save(self, *args, **kwargs):
        # Automatically set team_name before saving
        if self.is_our_team:
            self.team_name = self.match.get_team_display()
        else:
            self.team_name = self.match.opponent
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.match} - {self.team_name}"

class PlayerDetailedAction(models.Model):

    ACTION_TYPE_CHOICES = [
        ('offensive', 'Offensive'),
        ('defensive', 'Defensive'),
        ('set_piece', 'Set Piece'),
        ('transition', 'Transition'),
        ('discipline', 'Discipline'),
        ('goal_keeping', 'Goal Keeping'),
        ('general', 'General Game Event'),
    ]


    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="detailed_actions")
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name="player_detailed_actions")

    minutes_played = models.PositiveIntegerField(default=0)

    # CATEGORY 1: Offensive Actions
    shots_on_target_inside_box = models.PositiveIntegerField(default=0)
    shots_on_target_outside_box = models.PositiveIntegerField(default=0)
    shots_off_target_inside_box = models.PositiveIntegerField(default=0)
    shots_off_target_outside_box = models.PositiveIntegerField(default=0)
    successful_cross = models.PositiveIntegerField(default=0)
    unsuccessful_cross = models.PositiveIntegerField(default=0)
    missed_chance = models.PositiveIntegerField(default=0)
    bad_pass = models.PositiveIntegerField(default=0)
    touches_inside_box = models.PositiveIntegerField(default=0)

    # CATEGORY 2: Defensive Actions
    blocked_shots = models.PositiveIntegerField(default=0)
    aerial_duel_won = models.PositiveIntegerField(default=0)
    aerial_duel_lost = models.PositiveIntegerField(default=0)
    one_v_one_duel_won = models.PositiveIntegerField(default=0)
    one_v_one_duel_lost = models.PositiveIntegerField(default=0)
    ball_lost = models.PositiveIntegerField(default=0)

    # CATEGORY 3: Set Pieces
    corners = models.PositiveIntegerField(default=0)

    # CATEGORY 4: Transition
    offsides = models.PositiveIntegerField(default=0)

    # CATEGORY 5: Discipline
    fouls_committed = models.PositiveIntegerField(default=0)
    fouls_won = models.PositiveIntegerField(default=0)
    mistakes = models.PositiveIntegerField(default=0)
    yellow_cards = models.PositiveIntegerField(default=0, blank=True)
    red_cards = models.PositiveIntegerField(default=0, blank=True)

    # CATEGORY 6: Goalkeeping (if player is goalkeeper)
    saves = models.PositiveIntegerField(default=0)
    punches = models.PositiveIntegerField(default=0)
    drops = models.PositiveIntegerField(default=0)
    catches = models.PositiveIntegerField(default=0)
    penalties_saved = models.PositiveIntegerField(default=0)

    # CATEGORY 7: General Game Event
    is_our_team = models.BooleanField(default=True, help_text="Track only our team")
    created_at = models.DateTimeField(auto_now_add=True)
    action_type = models.CharField(
        max_length=20,
        choices=ACTION_TYPE_CHOICES,
        default='offensive',
        help_text="Category of the player's actions",
    )
    
    class Meta:
        verbose_name = "Player Detailed Action"
        verbose_name_plural = "Player Detailed Actions"
        unique_together = ('player', 'match')

    def __str__(self):
        return f"{self.player.name} - {self.match.date} - {self.match} - Actions"



