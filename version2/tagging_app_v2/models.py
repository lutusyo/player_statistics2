# tagging_app_v2/models.py
from django.db import models

from version2.tagging_app_v2.constants import BALL_ACTION_CHOICES, FOUL_OUTCOME
from version1.lineup_app.models import MatchLineup
from version1.matches_app.models import Match

class PassEvent_v2(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name="pass_events_v2")

    # Player who performs the action
    actor = models.ForeignKey(MatchLineup, on_delete=models.CASCADE, related_name="pass_events_as_actor")
    target = models.ForeignKey(MatchLineup, null=True, blank=True, on_delete=models.SET_NULL, related_name="pass_events_as_target")
    receiver = models.ForeignKey(MatchLineup, null=True, blank=True, on_delete=models.SET_NULL, related_name="pass_events_as_receiver")
    action_type = models.CharField(max_length=30, choices=BALL_ACTION_CHOICES)
    foul_outcome = models.CharField(max_length=30, choices=FOUL_OUTCOME, null=True, blank=True)
    timestamp = models.PositiveIntegerField(help_text="Match time in seconds", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp", "created_at"]

    def is_successful(self):
        """
        Successful if the receiver exists and
        receiver team is the same as actor team
        """
        if not self.receiver:
            return False

        return self.actor.team == self.receiver.team


    def __str__(self):
        actor = self.actor.player.name
        target = self.target.player.name if self.target else "—"
        receiver = self.receiver.player.name if self.receiver else "—"
        return f"{actor} → {target} ({self.action_type}) | Received: {receiver}"
    
    @property
    def minute(self):
        if self.timestamp:
            return self.timestamp // 60
        return 0
