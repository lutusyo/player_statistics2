# tagging_app_v2/models.py

from django.db import models
from tagging_app_v2.constants import BALL_ACTION_CHOICES
from lineup_app.models import MatchLineup
from matches_app.models import Match


class PassEvent_v2(models.Model):
    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE,
        related_name="pass_events_v2"
    )

    # Player who initiates the action (from lineup)
    actor = models.ForeignKey(
        MatchLineup,
        on_delete=models.CASCADE,
        related_name="events_as_actor"
    )

    action_type = models.CharField(
        max_length=20,
        choices=BALL_ACTION_CHOICES
    )

    # Receiver (can be OUR or OPPONENT lineup)
    receiver = models.ForeignKey(MatchLineup, null=True, blank=True, on_delete=models.SET_NULL, related_name="events_as_receiver")

    timestamp = models.PositiveIntegerField(
        help_text="Match time in seconds",
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp", "created_at"]


    
    def __str__(self):
        actor_name = self.actor.player.name if self.actor else "Unknown"
        receiver_name = self.receiver.player.name if self.receiver else "Unknown"
        return f"{actor_name} → {receiver_name} | {self.action_type}"
