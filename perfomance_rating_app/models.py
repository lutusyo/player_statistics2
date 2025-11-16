# perfomance_rating_app/models.py
from django.db import models
from players_app.models import Player
from matches_app.models import Match
from django.utils import timezone
import uuid
from teams_app.models import StaffMember


class PerformanceRating(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)

    # Core criteria ratings (1–5)
    attacking = models.IntegerField(null=True, blank=True)
    creativity = models.IntegerField(null=True, blank=True)
    defending = models.IntegerField(null=True, blank=True)
    tactical = models.IntegerField(null=True, blank=True)
    technical = models.IntegerField(null=True, blank=True)
    discipline = models.PositiveSmallIntegerField(default=5) 

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
    


class StaffPlayerRating(models.Model):
    """
    one overall rating (decimal) from a staff member for a player in a match.
    Each ( staff, player, match ) is unique so staff can not submit twice
    """
    staff = models.ForeignKey(StaffMember, on_delete=models.CASCADE, related_name="given_ratings")
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="staff_ratings")
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name="staff_ratings")

    # rating on 0..10 scale with one decimal place, eg 7.5
    rating = models.DecimalField(max_digits=4, decimal_places=1)
    comment = models.TextField(blank=True, null=True)

    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("staff", "player", "match")
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"{self.staff.name} --> {self.player.name} ({self.match}): {self.rating}"
    

class RatingToken(models.Model):
    """
    one token per ( staff, match). Token is single use and can expire. 
    We generate a token and Email it to a staff when they visit the link we validate token
    """
    staff = models.ForeignKey(StaffMember, on_delete=models.CASCADE, related_name="rating_tokens")
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name="rating_tokens")
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("staff", "match")

    def is_valid(self):

        if self.used:
            return False
        if self.expires_at and timezone.now() > self.expires_at:
            return False
        return True
    
    def mark_used(self):
        self.used = True
        self.used_at = timezone.now()
        self.save()









    