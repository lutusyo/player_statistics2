from django.db import models
from players_app.models import Player
from matches_app.models import Match
from teams_app.models import Team

class BodyPartChoices(models.TextChoices):
    LEFT = 'Left Foot', 'Left Foot'
    RIGHT = 'Right Foot', 'Right Foot'
    HEAD = 'Head', 'Head'
    OTHER = 'Other', 'Other'

class DeliveryTypeChoices(models.TextChoices):
    PASS = 'Pass', 'Pass'
    CROSS = 'Cross', 'Cross'
    LOOSE_BALL = 'Loose Ball', 'Loose Ball'
    CORNER = 'Corner', 'Corner'

class OutcomeChoices(models.TextChoices):
    OFF_TARGET = 'Off Target', 'Off Target'
    ON_TARGET_SAVED = 'On Target Saved', 'On Target Saved'
    ON_TARGET_GOAL = 'On Target Goal', 'On Target Goal'
    BLOCKED = 'Blocked', 'Blocked'
    ERROR = 'Player Error', 'Player Error'

    ### ATTEMPT TO GOAL TAGGING ###

class AttemptToGoal(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, related_name='attempts')

    minute = models.PositiveIntegerField()
    second = models.PositiveIntegerField()

    body_part = models.CharField(max_length=20, choices=BodyPartChoices.choices)
    delivery_type = models.CharField(max_length=20, choices=DeliveryTypeChoices.choices)
    
    outcome = models.CharField(max_length=30, choices=OutcomeChoices.choices)

    x = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="X position on pitch (0–100)")  # pitch zone
    y = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Y position on pitch (0–100)")

    assist_by = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, related_name='assists')
    pre_assist_by = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, related_name='pre_assists')

    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.player} | {self.outcome} | {self.minute}:{self.second:02d}"

    ### PASSING NETWORK ###

class PassEvent(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    from_player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='passes_made')
    to_player = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, related_name='passes_received')

    from_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='passes_from')
    to_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='passes_to')

    minute = models.PositiveIntegerField()
    second = models.PositiveIntegerField()

    x_start = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    y_start = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    x_end = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    y_end = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    is_successful = models.BooleanField(default=True)
    is_possession_regained = models.BooleanField(default=False)

    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.from_player} → {self.to_player or 'Loss'} at {self.minute}:{self.second:02d}"
