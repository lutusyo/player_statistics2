from django.db import models
from players_app.models import Player
from matches_app.models import Match
from teams_app.models import Team

class DeliveryTypeChoices(models.TextChoices):
    PASS = 'Pass', 'Pass'
    CROSS = 'Cross', 'Cross'
    LOOSE_BALL = 'Loose Ball', 'Loose Ball'
    CORNER = 'Corner', 'Corner'
    FREE_KICK = 'Free kick', 'Free kick'
    

class OutcomeChoices(models.TextChoices):
    OFF_TARGET = 'Off Target', 'Off Target'
    ON_TARGET_SAVED = 'On Target Saved', 'On Target Saved'
    ON_TARGET_GOAL = 'On Target Goal', 'On Target Goal'
    BLOCKED = 'Blocked', 'Blocked'
    PLAYER_ERROR = 'Player Error', 'Player Error'
    OWN_GOAL = 'Own Goal', 'Own Goal'

class LocationChoices(models.TextChoices):
    # Outside the penalty box
    OUTSIDE_BOX_LEFT = "Outside box left", "Outside box left"
    OUTSIDE_BOX_CENTER = "Outside box center", "Outside box center"
    OUTSIDE_BOX_RIGHT = "Outside box right", "Outside box right"

    # Inside the penalty box( excluding six-yard box and penalty spot)
    INSIDE_BOX_LEFT = "Inside box left", "Inside box left"
    INSIDE_BOX_CENTER = "Inside box center", "Inside box center"
    INSIDE_BOX_RIGHT = "Inside box right", "Inside box right"

    # Six-yard box(goal area)
    SIX_YARD_LEFT = "Six-yard box left", "Six-yard box left"
    SIX_YARD_CENTER = "Six-yard box center", "Six-yard box center"
    SIX_YARD_RIGHT = "Six-yard box right", "Six-yard box right"

    #Specific Locations
    PENALTY_SPOT = "Penalty spot", "Penalty spot"
    LONG_RANGE = "Long Range", "Long Range"
    OTHER = "Other", "Other"

class BodyPartChoices(models.TextChoices):
    RIGHT_FOOT = 'Right Foot', 'Right Foot'
    LEFT_FOOT = 'Left Foot', 'Left Foot'
    HEADER = 'Header', 'Header'
    OTHER = 'Other', 'Other'


    # ATTEMPT TO GOAL TAGGING
class AttemptToGoal(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)  # Team making the attempt
    player = models.ForeignKey(
        Player, on_delete=models.SET_NULL, null=True, blank=True, related_name='attempts'
    )
    minute = models.PositiveIntegerField(default=0)
    second = models.PositiveIntegerField(default=0)
    delivery_type = models.CharField(max_length=20, choices=DeliveryTypeChoices.choices)
    outcome = models.CharField(max_length=30, choices=OutcomeChoices.choices)

    body_part = models.CharField(max_length=20, choices=BodyPartChoices.choices, default=BodyPartChoices.RIGHT_FOOT)
    location_tag = models.CharField(max_length=30, choices=LocationChoices.choices, default=LocationChoices.LONG_RANGE, null=False, blank=False)

    x = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    y = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    assist_by = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, related_name='assists')
    pre_assist_by = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, related_name='pre_assists')
    
    is_opponent = models.BooleanField(default=False, help_text='This was attempt made by opponent')
    is_own_goal = models.BooleanField(default=False, help_text='Mark if this attempt is an own Goal')
    own_goal_for = models.ForeignKey(
        Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='benefited_from_own_goals',
        help_text="If this is an own goal, which team benefits from it?"
    )

    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        player_name = self.player.name if self.player else "Unknown"
        return f"{player_name} | {self.outcome} | {self.minute}:{self.second:02d}"


    # PASSING NETWORK
class PassEvent(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    from_player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='passes_made', null=True, blank=True)
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

    # BALL OUT OF PLAY
    is_ball_out = models.BooleanField(default=False)
    ball_out_by = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, related_name='player_who_kick_the_ball_out')
    throw_in_team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True)
    throw_in_player = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, related_name='player_who_make_a_throw_in')

    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.from_player} → {self.to_player or 'Loss'} at {self.minute}:{self.second:02d}"
    


class GoalkeeperDistributionEvent(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    goalkeeper = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='gk_distributions')
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    minute = models.PositiveIntegerField()
    second = models.PositiveIntegerField()

    method = models.CharField(max_length=30, choices=[
        ('from_feet', 'From Feet'),
        ('from_hands', 'From Hands'),
        ('throw', 'Throw Distribution'),
    ])

    detail = models.CharField(max_length=30, choices=[
        # Distribution with Feet
        ('play_onto', 'Play Onto'),
        ('play_into', 'Play Into'),
        ('play_around', 'Play Around'),
        ('play_beyond', 'Play Beyond'),
        ('other_feet', 'Other (Feet)'),

        # Distribution from Hands ( kicks )
        ('side_kick', 'Side Kick'),
        ('from_hands', 'From Hands'),
        ('drop_kick', 'Drop Kick'),

        # Dstribution from Hands  ( Throws ) 
        ('over_arm', 'Over Arm'),
        ('under_arm', 'Under Arm'),
        ('side_arm', 'Side Arm'),
        ('chest_pass', 'Chest Pass'),
    ])

    is_complete = models.BooleanField(default=True)
    is_goal_conceded = models.BooleanField(default=False)

    involvement_duration = models.FloatField(
        help_text="Duration in seconds the goalkeeper had the ball",
        null=True, blank=True
    )

    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.goalkeeper.name} - {self.method} ({self.minute}:{self.second:02d})"
