from django.db import models
from apps.core.constants import BALL_ACTION_CHOICES, FOUL_OUTCOME
from version1.lineup_app.models import MatchLineup
from version1.matches_app.models import Match

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q

from version1.matches_app.models import Match
from version1.teams_app.models import Team
from version2.tagging_app_v2.models import PassEvent_v2
from version1.lineup_app.models import MatchLineup, Substitution
from version2.tagging_app_v2.forms import PassEventV2Form
from version3.tagging_app_v3.constants import MatchPeriod, EventType, DeliveryTypeChoices, OutcomeChoices, BodyPartChoices, LocationChoices

class MatchEvent(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name="events")
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    period = models.CharField(
        max_length=5,
        choices=MatchPeriod.choices,
        default=MatchPeriod.FIRST_HALF
    )

    # WHO
    actor = models.ForeignKey(
        MatchLineup,
        on_delete=models.CASCADE,
        related_name="events_as_actor"
    )

    receiver = models.ForeignKey(
        MatchLineup,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="events_as_receiver"
    )

    # EVENT TYPE (SIMPLIFIED)
    event_type = models.CharField(
        max_length=30,
        choices=EventType.choices
    )

    # TIME
    minute = models.PositiveIntegerField(default=0)
    second = models.PositiveIntegerField(default=0)

    # POSITION
    x = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    y = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    # BALL ACTION
    action_type = models.CharField(
        max_length=30,
        choices=BALL_ACTION_CHOICES,
        null=True,
        blank=True
    )

    foul_outcome = models.CharField(
        max_length=30,
        choices=FOUL_OUTCOME,
        null=True,
        blank=True
    )

    # SHOT
    delivery_type = models.CharField(
        max_length=20,
        choices=DeliveryTypeChoices.choices,
        null=True,
        blank=True
    )

    outcome = models.CharField(
        max_length=30,
        choices=OutcomeChoices.choices,
        null=True,
        blank=True
    )

    body_part = models.CharField(
        max_length=20,
        choices=BodyPartChoices.choices,
        null=True,
        blank=True
    )

    location_tag = models.CharField(
        max_length=30,
        choices=LocationChoices.choices,
        null=True,
        blank=True
    )

    # ASSISTS (manual system)
    assist_by = models.ForeignKey(
        MatchLineup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assists"
    )

    pre_assist_by = models.ForeignKey(
        MatchLineup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pre_assists"
    )

    # SPECIAL
    is_own_goal = models.BooleanField(default=False)

    own_goal_for = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="v3_benefited_from_own_goals"
    )

    # MEDIA
    video_clip = models.FileField(upload_to='event_clips/', null=True, blank=True)
    thumbnail = models.ImageField(upload_to='event_thumbnails/', null=True, blank=True)

    # META
    created_at = models.DateTimeField(auto_now_add=True)