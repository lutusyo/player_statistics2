from django.db import models
from players_app.models import Player
from matches_app.models import Match
from teams_app.models import Team


class PositionChoices(models.TextChoices):
    GK = 'GK', 'Goalkeeper'
    RB = 'RB', 'Right Back'
    RCB = 'RCB', 'Right Center Back'
    LCB = 'LCB', 'Left Center Back'
    LB = 'LB', 'Left Back'
    RM = 'RM', 'Right Midfielder'
    CM = 'CM', 'Central Midfielder'
    LM = 'LM', 'Left Midfielder'
    RW = 'RW', 'Right Winger'
    LW = 'LW', 'Left Winger'
    ST = 'ST', 'Striker'
    # Optional SUB if you want to keep it
    SUB = 'SUB', 'Substitute'


class MatchLineup(models.Model):
    # A record of a single player's registration for a specific match.
    # We keep one MatchLineup row per squad member for a match (starting XI + subs + bench entries).
    match = models.ForeignKey(Match, on_delete=models.CASCADE, null=True, blank=True, help_text='Match this player is registered for')
    player = models.ForeignKey(Player, on_delete=models.CASCADE, null=True, blank=True, help_text='Player registered for this match')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True, help_text='Team this player belongs to (optional if you derive from Player)')
    is_starting = models.BooleanField(default=False, help_text='True if this player is in the starting eleven')

    position = models.CharField(max_length=5, choices=PositionChoices.choices, default=PositionChoices.SUB, blank=True, null=True)
    pod_number = models.CharField(max_length=20, null=True, blank=True, default='Demo', help_text="GPS Pod number assigned to the player in this match")
    time_in = models.PositiveSmallIntegerField(null=True,blank=True, help_text='Minute the player entered the match (e.g. 0 for starting XI or 1). Null = not yet played.')

    time_out = models.PositiveSmallIntegerField(null=True, blank=True, help_text='Minute the player went out of the match. Null = still on pitch or not used.')

    minutes_played = models.PositiveSmallIntegerField(default=0, help_text='Total minutes this player played in the match; calculated after substitutions or when the match ends.')

    # A small administrative field to help ordering lineup rows in the UI if you want
    order = models.PositiveSmallIntegerField(null=True, blank=True, help_text='Optional ordering key to control display order on UI.')

    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('match', 'player', 'pod_number'),)  # ensure each player appears only once per match
        ordering = ['order', 'player__name']

    def __str__(self):
        # Useful display in admin and debug logs
        return f"{self.match} — {self.player} (start={self.is_starting}) - {self.pod_number}"

    def calculate_minutes_played(self, final_minute=None):
        """
        Calculate minutes played for this lineup row.

        - If both time_in and time_out are present: minutes = time_out - time_in
        - If time_out is missing but final_minute provided (match ended): minutes = final_minute - time_in
        - If time_in missing -> 0
        - Return 0 for negative or invalid ranges.

        final_minute: integer or None. When you call this at match end, pass the ending minute.
        """
        # If the player never entered the match we cannot compute minutes
        if self.time_in is None:
            return 0

        # Determine the end minute to use
        end_minute = None
        if self.time_out is not None:
            end_minute = self.time_out
        elif final_minute is not None:
            end_minute = final_minute

        if end_minute is None:
            # No end minute known yet (player still on pitch and match still running)
            return 0

        # Calculate and guard against negative results
        mp = end_minute - self.time_in
        return mp if mp > 0 else 0

class Substitution(models.Model):
    # A single substitution event: which player went out, which came in, and at what minute
    match = models.ForeignKey(Match, on_delete=models.CASCADE, help_text='Match where substitution happened')
    player_out = models.ForeignKey(MatchLineup, related_name='substituted_out', on_delete=models.CASCADE, help_text='Lineup row for the player who left the pitch')
    player_in = models.ForeignKey(MatchLineup, related_name='substituted_in', on_delete=models.CASCADE, help_text='Lineup row for the player who came on')

    minute = models.PositiveSmallIntegerField(help_text='Minute when the substitution occurred')
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.match} | {self.player_out.player} -> {self.player_in.player} @{self.minute}"