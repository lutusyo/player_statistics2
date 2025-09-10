from django.db import models
from players_app.models import Player
from matches_app.models import Match

class PlayerDefensiveStats(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)

    aerial_duel_won = models.PositiveIntegerField(default=0)
    aerial_duel_lost = models.PositiveIntegerField(default=0)

    tackle_won = models.PositiveIntegerField(default=0)
    tackle_lost = models.PositiveIntegerField(default=0)

    physical_duel_won = models.PositiveIntegerField(default=0)
    physical_duel_lost = models.PositiveIntegerField(default=0)

    duel_1v1_won_att = models.PositiveIntegerField(default=0)
    duel_1v1_lost_att = models.PositiveIntegerField(default=0)
    duel_1v1_won_def = models.PositiveIntegerField(default=0)
    duel_1v1_lost_def = models.PositiveIntegerField(default=0)

    foul_committed = models.PositiveIntegerField(default=0)
    foul_won = models.PositiveIntegerField(default=0)

    corner = models.PositiveIntegerField(default=0)
    offside = models.PositiveIntegerField(default=0)

    yellow_card = models.PositiveIntegerField(default=0)
    red_card = models.PositiveIntegerField(default=0)

    line_breaks_completed = models.IntegerField(default=0)
    defensive_line_breaks = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.player.name} - {self.match}"
