# actions_app/models.py
from django.db import models
from matches_app.models import Match

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
