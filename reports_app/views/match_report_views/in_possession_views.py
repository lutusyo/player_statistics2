from io import BytesIO
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse, HttpResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from django.db.models import Count, Q
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from matches_app.models import Match
from players_app.models import Player
from teams_app.models import Team
from lineup_app.models import MatchLineup
from tagging_app.models import AttemptToGoal, DeliveryTypeChoices, OutcomeChoices, BodyPartChoices, LocationChoices, PassEvent
from tagging_app.utils.attempt_to_goal_utils import get_match_full_context
import json
import traceback
from collections import defaultdict
import csv
import io
import pandas as pd
import matplotlib.pyplot as plt
# from mplsoccer import Pitch  # ❌ Commented out
import os
# ReportLab (PDF)
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Image, Spacer
from reportlab.lib.styles import getSampleStyleSheet
# Excel
from openpyxl import Workbook
# Matplotlib (server-side)
import matplotlib
matplotlib.use('Agg')  # non-GUI backend for servers
import matplotlib.pyplot as plt
from tagging_app.utils.pass_network_utils import get_pass_network_context  # ✅ add this
import base64

def create_shotmap_base64(attempts_queryset):
    if attempts_queryset.count() == 0:
        return None

    df = pd.DataFrame(list(attempts_queryset.values("x", "y", "outcome")))

    color_map = {
        'On Target Goal': '#00ff00',
        'On Target Saved': '#1e90ff',
        'Off Target': '#ffcc00',
        'Blocked': '#ff8c00',
        'Player Error': '#ff0000',
    }

    df["color"] = df["outcome"].map(color_map).fillna("#ffffff")

    fig, ax = plt.subplots(figsize=(13, 8.5))
    fig.set_facecolor('#22312b')

    # ❌ Commented out mplsoccer Pitch
    # pitch = Pitch(
    #     pitch_type='statsbomb',
    #     pitch_color='#22312b',
    #     line_color='#7d5ccc'
    # )
    # pitch.draw(ax=ax)

    plt.scatter(
        df['x'], df['y'],
        c=df['color'],
        s=120,
        edgecolors='black',
        linewidth=0.5,
        alpha=0.85,
    )

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
    plt.close(fig)
    buffer.seek(0)

    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def attempt_to_goal_dashboard(request, match_id, return_context=False):
    match = get_object_or_404(Match, id=match_id)
    
    home_team_id = match.home_team.id
    away_team_id = match.away_team.id

    context = get_match_full_context(match_id, home_team_id)

    # Players from the lineup
    home_lineup = MatchLineup.objects.filter(match=match, team_id=home_team_id).select_related("player")
    home_players = [entry.player for entry in home_lineup]

    away_lineup = MatchLineup.objects.filter(match=match, team_id=away_team_id).select_related("player")
    away_players = [entry.player for entry in away_lineup]

    # Build outcomes_matrix (per player per outcome)
    outcomes_matrix = {}
    for player in home_players + away_players:
        counts = (
            AttemptToGoal.objects.filter(player=player, match=match)
            .values("outcome")
            .annotate(count=Count("outcome"))
        )
        outcomes_matrix[player.id] = {row["outcome"]: row["count"] for row in counts}

    # Separate attempts
    home_attempts = AttemptToGoal.objects.filter(match=match, team_id=home_team_id).select_related("player", "team").order_by("minute", "second")
    away_attempts = AttemptToGoal.objects.filter(match=match, team_id=away_team_id).select_related("player", "team").order_by("minute", "second")

    # Goals
    goals = AttemptToGoal.objects.filter(match=match).filter(
        Q(outcome="On Target Goal") | Q(is_own_goal=True)
    ).select_related("player", "assist_by", "pre_assist_by", "team", "own_goal_for").order_by("minute", "second")

    # Delivery types totals
    home_total_delivery_types = home_attempts.values('delivery_type').annotate(total=Count('id')).order_by('delivery_type')
    away_total_delivery_types = away_attempts.values('delivery_type').annotate(total=Count('id')).order_by('delivery_type')

    # Summary stats
    home_summary = {
        "goals": home_attempts.filter(Q(outcome="On Target Goal") | Q(is_own_goal=True)).count(),
        "on_target_saved": home_attempts.filter(outcome="On Target Saved").count(),
        "off_target": home_attempts.filter(outcome="Off Target").count(),
        "blocked": home_attempts.filter(outcome="Blocked").count(),
        "incomplete": home_attempts.filter(outcome="Player Error").count(),
    }
    home_summary["on_target_total"] = home_summary["goals"] + home_summary["on_target_saved"]

    away_summary = {
        "goals": away_attempts.filter(Q(outcome="On Target Goal") | Q(is_own_goal=True)).count(),
        "on_target_saved": away_attempts.filter(outcome="On Target Saved").count(),
        "off_target": away_attempts.filter(outcome="Off Target").count(),
        "blocked": away_attempts.filter(outcome="Blocked").count(),
        "incomplete": away_attempts.filter(outcome="Player Error").count(),
    }
    away_summary["on_target_total"] = away_summary["goals"] + away_summary["on_target_saved"]

    # Filter by categories
    home_shots_on_target = home_attempts.filter(outcome__in=[OutcomeChoices.ON_TARGET_GOAL, OutcomeChoices.ON_TARGET_SAVED])
    home_shots_off_target = home_attempts.filter(outcome=OutcomeChoices.OFF_TARGET)
    home_blocked_shots = home_attempts.filter(outcome=OutcomeChoices.BLOCKED)
    home_player_errors = home_attempts.filter(outcome=OutcomeChoices.PLAYER_ERROR).exclude(body_part=BodyPartChoices.OTHER)
    home_unsuccessful_crosses = home_attempts.filter(outcome=OutcomeChoices.PLAYER_ERROR, body_part=BodyPartChoices.OTHER, delivery_type=DeliveryTypeChoices.CROSS).select_related("assist_by", "player")
    home_unsuccessful_cross_assisters = home_unsuccessful_crosses.exclude(assist_by__isnull=True).values("assist_by__id", "assist_by__name").annotate(total=Count("id")).order_by("-total")
    home_corners = home_attempts.filter(delivery_type=DeliveryTypeChoices.CORNER)
    home_crosses = home_attempts.filter(delivery_type=DeliveryTypeChoices.CROSS)
    home_effective_loose_ball = home_attempts.filter(delivery_type=DeliveryTypeChoices.LOOSE_BALL)
    home_effective_pass = home_attempts.filter(delivery_type=DeliveryTypeChoices.PASS)

    away_shots_on_target = away_attempts.filter(outcome__in=[OutcomeChoices.ON_TARGET_GOAL, OutcomeChoices.ON_TARGET_SAVED])
    away_shots_off_target = away_attempts.filter(outcome=OutcomeChoices.OFF_TARGET)
    away_blocked_shots = away_attempts.filter(outcome=OutcomeChoices.BLOCKED)
    away_player_errors = away_attempts.filter(outcome=OutcomeChoices.PLAYER_ERROR).exclude(body_part=BodyPartChoices.OTHER)
    away_unsuccessful_crosses = away_attempts.filter(outcome=OutcomeChoices.PLAYER_ERROR, body_part=BodyPartChoices.OTHER, delivery_type=DeliveryTypeChoices.CROSS).select_related("assist_by", "player")
    away_unsuccessful_cross_assisters = away_unsuccessful_crosses.exclude(assist_by__isnull=True).values("assist_by__id", "assist_by__name").annotate(total=Count("id")).order_by("-total")
    away_corners = away_attempts.filter(delivery_type=DeliveryTypeChoices.CORNER)
    away_crosses = away_attempts.filter(delivery_type=DeliveryTypeChoices.CROSS)
    away_effective_loose_ball = away_attempts.filter(delivery_type=DeliveryTypeChoices.LOOSE_BALL)
    away_effective_pass = away_attempts.filter(delivery_type=DeliveryTypeChoices.PASS)

    # Shotmaps
    home_shotmap = create_shotmap_base64(home_attempts)
    away_shotmap = create_shotmap_base64(away_attempts)

    # Update context
    context.update({
        "home_players": home_players,
        "away_players": away_players,
        "outcomes_matrix": outcomes_matrix,

        "home_attempts": home_attempts,
        "away_attempts": away_attempts,

        "home_summary": home_summary,
        "away_summary": away_summary,
        "goals": goals,
        "match": match,

        "home_total_delivery_types": home_total_delivery_types,
        "away_total_delivery_types": away_total_delivery_types,

        "home_shots_on_target": home_shots_on_target,
        "home_shots_off_target": home_shots_off_target,
        "home_blocked_shots": home_blocked_shots,
        "home_player_errors": home_player_errors,
        "home_unsuccessful_cross_assisters": home_unsuccessful_cross_assisters,
        "home_corners": home_corners,
        "home_crosses": home_crosses,
        "home_effective_loose_ball": home_effective_loose_ball,
        "home_effective_pass": home_effective_pass,

        "away_shots_on_target": away_shots_on_target,
        "away_shots_off_target": away_shots_off_target,
        "away_blocked_shots": away_blocked_shots,
        "away_player_errors": away_player_errors,
        "away_unsuccessful_cross_assisters": away_unsuccessful_cross_assisters,
        "away_corners": away_corners,
        "away_crosses": away_crosses,
        "away_effective_loose_ball": away_effective_loose_ball,
        "away_effective_pass": away_effective_pass,

        "home_shotmap": home_shotmap,
        "away_shotmap": away_shotmap,

        "home_team": match.home_team,
        "away_team": match.away_team,
    })

    if return_context:
        return context

    return render(request, "reports_app/match_report_templates/4_in_possession/attempt_to_goal.html", context)
    
def pass_network_dashboard(request, match_id, return_context=False):
    match = get_object_or_404(Match, id=match_id)

    home_pass = get_pass_network_context(match, match.home_team.id)
    away_pass = get_pass_network_context(match, match.away_team.id)

    context = {
        "match": match,
        "home_team": match.home_team,
        "away_team": match.away_team,

        "home_pass": home_pass,
        "away_pass": away_pass,
    }

    if return_context:
        return context

    return render(request, "reports_app/match_report_templates/4_in_possession/pass_network.html", context )




