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
    
    our_team_id = request.GET.get("our_team_id") or match.home_team.id
    try:
        our_team_id = int(our_team_id)
    except ValueError:
        our_team_id = match.home_team.id

    context = get_match_full_context(match_id, our_team_id)

    # ✅ Players from the lineup
    lineup = MatchLineup.objects.filter(match=match, team_id=our_team_id).select_related("player")
    players = [entry.player for entry in lineup]

    # ✅ Build outcomes_matrix (per player per outcome)
    outcomes_matrix = {}
    for player in players:
        counts = (
            AttemptToGoal.objects.filter(player=player, match=match)
            .values("outcome")
            .annotate(count=Count("outcome"))
        )
        outcomes_matrix[player.id] = {row["outcome"]: row["count"] for row in counts}

    # ✅ Separate attempts (move outside the loop)
    our_attempts = (
        AttemptToGoal.objects.filter(match=match, team_id=our_team_id)
        .select_related("player", "team")
        .order_by("minute", "second")
    )
    opponent_attempts = (AttemptToGoal.objects.filter(match=match)
        .exclude(team_id=our_team_id)
        .select_related("player", "team")
        .order_by("minute", "second")
    )

    # ✅ Add goals (move outside loop)
    goals = AttemptToGoal.objects.filter(match=match).filter(
        Q(outcome="On Target Goal") | Q(is_own_goal=True)
    ).select_related(
        "player", "assist_by", "pre_assist_by", "team", "own_goal_for"
    ).order_by("minute", "second")


    our_attempts = AttemptToGoal.objects.filter(match=match, is_opponent=False)

    # Get totals for each delivery type
    total_delivery_types = (
        our_attempts.values('delivery_type')
        .annotate(total=Count('id'))
        .order_by('delivery_type')
    )

    # ✅ Compute summaries
    our_summary = {
        "goals": our_attempts.filter(Q(outcome="On Target Goal") | Q(is_own_goal=True)).count(),
        "on_target_saved": our_attempts.filter(outcome="On Target Saved").count(),
        "off_target": our_attempts.filter(outcome="Off Target").count(),
        "blocked": our_attempts.filter(outcome="Blocked").count(),
        "incomplete": our_attempts.filter(outcome="Player Error").count(),
    }

    our_summary["on_target_total"] = our_summary["goals"] + our_summary["on_target_saved"]

    opponent_summary = {
        "goals": opponent_attempts.filter(Q(outcome="On Target Goal") | Q(is_own_goal=True)).count(),
        "on_target": opponent_attempts.filter(outcome="On Target").count(),
        "on_target_save": opponent_attempts.filter(outcome="On Target Save").count(),
        "off_target": opponent_attempts.filter(outcome="Off Target").count(),
        "blocked": opponent_attempts.filter(outcome="Blocked").count(),
        "incomplete": opponent_attempts.filter(outcome="Incomplete").count(),
    }

    opponent_summary["on_target_total"] = opponent_summary["goals"] + opponent_summary["on_target_save"]

##############################################################################################################################
    # Filter by categories
    our_shots_on_target = our_attempts.filter(outcome__in=[OutcomeChoices.ON_TARGET_GOAL, OutcomeChoices.ON_TARGET_SAVED])
    our_shots_off_target = our_attempts.filter(outcome=OutcomeChoices.OFF_TARGET)
    our_blocked_shots = our_attempts.filter(outcome=OutcomeChoices.BLOCKED)
    our_player_errors = our_attempts.filter(outcome=OutcomeChoices.PLAYER_ERROR).exclude(body_part=BodyPartChoices.OTHER)
    our_unsuccessful_crosses = our_attempts.filter(
        outcome=OutcomeChoices.PLAYER_ERROR, 
        body_part=BodyPartChoices.OTHER, 
        delivery_type=DeliveryTypeChoices.CROSS
        ).select_related("assist_by", "player")
    our_unsuccessful_cross_assisters = (our_unsuccessful_crosses
    .exclude(assist_by__isnull=True)
    .values(
        "assist_by__id",
        "assist_by__name"
    )
    .annotate(total=Count("id"))
    .order_by("-total")
    )

    our_corners = our_attempts.filter(delivery_type=DeliveryTypeChoices.CORNER)
    our_crosses = our_attempts.filter(delivery_type=DeliveryTypeChoices.CROSS)
    our_effective_loose_ball = our_attempts.filter(delivery_type=DeliveryTypeChoices.LOOSE_BALL)
    our_effective_pass = our_attempts.filter(delivery_type=DeliveryTypeChoices.PASS)

    # Filter by categories for opponents
    opponent_attempts = AttemptToGoal.objects.filter(match=match, is_opponent=True)     # opponents team attempts

    opponent_shots_on_target = opponent_attempts.filter(outcome__in=[OutcomeChoices.ON_TARGET_GOAL, OutcomeChoices.ON_TARGET_SAVED])
    opponent_shots_off_target = opponent_attempts.filter(outcome=OutcomeChoices.OFF_TARGET)
    opponent_blocked_shots = opponent_attempts.filter(outcome=OutcomeChoices.BLOCKED)
    opponent_player_errors = opponent_attempts.filter(outcome=OutcomeChoices.PLAYER_ERROR).exclude(body_part=BodyPartChoices.OTHER)
    opponent_unsuccessful_crosses = opponent_attempts.filter(
        outcome=OutcomeChoices.PLAYER_ERROR, 
        body_part=BodyPartChoices.OTHER, 
        delivery_type=DeliveryTypeChoices.CROSS
        ).select_related("assist_by", "player")
    
    opponent_unsuccessful_cross_assisters = (opponent_unsuccessful_crosses
    .exclude(assist_by__isnull=True)
    .values(
        "assist_by__id",
        "assist_by__name"
    )
    .annotate(total=Count("id"))
    .order_by("-total")
    )    

    opponent_corners = opponent_attempts.filter(delivery_type=DeliveryTypeChoices.CORNER)
    opponent_crosses = opponent_attempts.filter(delivery_type=DeliveryTypeChoices.CROSS)
    opponent_effective_loose_ball = opponent_attempts.filter(delivery_type=DeliveryTypeChoices.LOOSE_BALL)
    opponent_effective_pass = opponent_attempts.filter(delivery_type=DeliveryTypeChoices.PASS)

    # ❌ Commented out mplsoccer shotmaps
    our_shotmap = create_shotmap_base64(our_attempts)
    opponent_shotmap = create_shotmap_base64(opponent_attempts)

    # ✅ Update context
    context.update({
        "players": players,
        "outcomes_matrix": outcomes_matrix,
        "our_attempts": our_attempts,
        "opponent_attempts": opponent_attempts,
        "our_summary": our_summary,
        "opponent_summary": opponent_summary,
        "goals": goals,
        "match": match,
        'total_delivery_types': total_delivery_types,

        "match": match,
        "our_shots_on_target": our_shots_on_target,
        "our_shots_off_target": our_shots_off_target,
        "our_blocked_shots": our_blocked_shots,
        "our_player_errors": our_player_errors,
        "our_unsuccessful_crosses": our_unsuccessful_crosses,
        "our_unsuccessful_cross_assisters": our_unsuccessful_cross_assisters,

        "our_corners": our_corners,
        "our_crosses": our_crosses,
        "our_effective_loose_ball": our_effective_loose_ball,
        "our_effective_pass": our_effective_pass,

        "opponent_shots_on_target": opponent_shots_on_target,
        "opponent_shots_off_target": opponent_shots_off_target,
        "opponent_blocked_shots": opponent_blocked_shots,
        "opponent_player_errors": opponent_player_errors,
        "opponent_unsuccessful_crosses": opponent_unsuccessful_crosses,
        "opponent_unsuccessful_cross_assisters": opponent_unsuccessful_cross_assisters,

        "opponent_corners": opponent_corners,
        "opponent_crosses": opponent_crosses,
        "opponent_effective_loose_ball": opponent_effective_loose_ball,
        "opponent_effective_pass": opponent_effective_pass,

        "home_team": match.home_team,
        "away_team": match.away_team,
    })

    context["our_shotmap"] = our_shotmap
    context["opponent_shotmap"] = opponent_shotmap

    if return_context:
        return context

    return render(request, "reports_app/match_report_templates/4_in_possession/attempt_to_goal.html", context)


def pass_network_dashboard(request, match_id, return_context=False):
    match = get_object_or_404(Match, id=match_id)  # ✅ Add this line
    context = get_pass_network_context(match)      # ✅ Use the Match object, not match_id
    context['match'] = match                       # ✅ Add match to context explicitly

    if return_context:
        return context

    return render(request, "reports_app/match_report_templates/4_in_possession/pass_network.html", context)
