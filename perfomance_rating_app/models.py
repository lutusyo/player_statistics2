# perfomance_rating_app/models.py
from django.db import models
from players_app.models import Player
from matches_app.models import Match

class PerformanceRating(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)

    # Core criteria ratings (1–5)
    attacking = models.IntegerField(null=True, blank=True)
    creativity = models.IntegerField(null=True, blank=True)
    defending = models.IntegerField(null=True, blank=True)
    tactical = models.IntegerField(null=True, blank=True)
    technical = models.IntegerField(null=True, blank=True)

    is_computed = models.BooleanField(default=False)
    is_manual = models.BooleanField(default=False)  # Added for manual override option
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('player', 'match')

    def overall(self):
        values = [self.attacking, self.creativity, self.defending, self.tactical, self.technical]
        values = [v for v in values if v is not None]
        return round(sum(values) / len(values), 2) if values else None

    def __str__(self):
        return f"Rating for {self.player} in {self.match}"


