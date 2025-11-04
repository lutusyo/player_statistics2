# reports_app/views/match_report_view.py
from io import BytesIO
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from matches_app.models import Match
from lineup_app.models import MatchLineup
from defensive_app.models import PlayerDefensiveStats 
from tagging_app.models import AttemptToGoal, PassEvent, GoalkeeperDistributionEvent, DeliveryTypeChoices, OutcomeChoices, BodyPartChoices, LocationChoices
from teams_app.models import Team

# PDF generation - using reportlab for a robust result
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from django.db.models import Count, Q
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from players_app.models import Player
from tagging_app.utils.attempt_to_goal_utils import get_match_full_context
import json
import traceback

#2
from tagging_app.utils.pass_network_utils import get_pass_network_context  # ✅ add this


def match_report_html(request, match_id):
    """Display match report in HTML."""

    # 1. atempt_to_goal data
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
    opponent_attempts = (
        AttemptToGoal.objects.filter(match=match).exclude(team_id=our_team_id)
        .select_related("player", "team")
        .order_by("minute", "second")
    )

    # ✅ Add goals (move outside loop)
    goals = AttemptToGoal.objects.filter(match=match).filter(
        Q(outcome="On Target Goal") | Q(is_own_goal=True)
    ).select_related(
        "player", "assist_by", "pre_assist_by", "team", "own_goal_for"
    ).order_by("minute", "second")


    our_team_attempts = AttemptToGoal.objects.filter(match_id=match_id, is_opponent=False)

    # Get totals for each delivery type
    total_delivery_types = (
        our_team_attempts.values('delivery_type')
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

    #opponent_summary["on_target_total"] = opponent_summary["goals"] + opponent_summary["on_target_save"]



##############################################################################################################################
    our_attempts = AttemptToGoal.objects.filter(match=match, is_opponent=False)   # our team attempts
    
    # Filter by categories


    our_shots_on_target = our_attempts.filter(outcome__in=[OutcomeChoices.ON_TARGET_GOAL, OutcomeChoices.ON_TARGET_SAVED])
    our_shots_off_target = our_attempts.filter(outcome=OutcomeChoices.OFF_TARGET)
    our_blocked_shots = our_attempts.filter(outcome=OutcomeChoices.BLOCKED)
    our_player_errors = our_attempts.filter(outcome=OutcomeChoices.PLAYER_ERROR)

    our_corners = our_attempts.filter(delivery_type=DeliveryTypeChoices.CORNER)
    our_crosses = our_attempts.filter(delivery_type=DeliveryTypeChoices.CROSS)
    our_effective_loose_ball = our_attempts.filter(delivery_type=DeliveryTypeChoices.LOOSE_BALL)
    our_effective_pass = our_attempts.filter(delivery_type=DeliveryTypeChoices.PASS)

        
   # opponent_attempts = AttemptToGoal.objects.filter(match=match, is_opponent=True)     # opponents team attempts
    # Filter by categories
    #opponent_shots_on_target = opponent_attempts.filter(outcome__in=[OutcomeChoices.ON_TARGET_GOAL, OutcomeChoices.ON_TARGET_SAVED])
    #opponent_shots_off_target = opponent_attempts.filter(outcome=OutcomeChoices.OFF_TARGET)
    #opponent_blocked_shots = opponent_attempts.filter(outcome=OutcomeChoices.BLOCKED)
    #opponent_player_errors = opponent_attempts.filter(outcome=OutcomeChoices.PLAYER_ERROR)

    #opponent_corners = opponent_attempts.filter(delivery_type=DeliveryTypeChoices.CORNER)
    #opponent_crosses = opponent_attempts.filter(delivery_type=DeliveryTypeChoices.CROSS)


    

    # Determine which team is our team (you may prefer to pass team id instead)
    our_team = match.home_team if match.home_team.team_type == 'OUR_TEAM' else match.away_team
    opponent = match.away_team if our_team == match.home_team else match.home_team

    # Gather data
    lineup = MatchLineup.objects.filter(match=match, team=our_team).order_by('order')
    attempts = AttemptToGoal.objects.filter(match=match, team=our_team).order_by('minute', 'second')
    passes = PassEvent.objects.filter(match=match, from_team=our_team).order_by('minute', 'second')
    gk_dist = GoalkeeperDistributionEvent.objects.filter(match=match, team=our_team).order_by('minute', 'second')
    defensive_stats = PlayerDefensiveStats.objects.filter(match=match, player__team=our_team)



    context = {
        "match": match,
        "our_team": our_team,
        "opponent": opponent,
        "lineup": lineup,
        "attempts": attempts,
        "passes": passes,
        "gk_dist": gk_dist,
        "defensive_stats": defensive_stats,
    }


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

        "our_corners": our_corners,
        "our_crosses": our_crosses,
        "our_effective_loose_ball": our_effective_loose_ball,
        "our_effective_pass": our_effective_pass,
        "home_team": match.home_team,
        "away_team": match.away_team,
    })


    return render(request, "reports_app/match_report.html", context)

############################### PASS NETWORK  #######################################################
 
    
    


def download_match_report_pdf(request, match_id):
    """Generate a PDF version of the team report (simple, printable layout)."""
    match = get_object_or_404(Match, id=match_id)
    our_team = match.home_team if match.home_team.team_type == 'OUR_TEAM' else match.away_team
    opponent = match.away_team if our_team == match.home_team else match.home_team

    lineup = MatchLineup.objects.filter(match=match, team=our_team).order_by('order')
    attempts = AttemptToGoal.objects.filter(match=match, team=our_team).order_by('minute', 'second')
    defensive_stats = PlayerDefensiveStats.objects.filter(match=match, player__team=our_team)

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Header
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width / 2, height - 50, f"{our_team.name} vs {opponent.name}")
    p.setFont("Helvetica", 11)
    p.drawCentredString(width / 2, height - 68, f"{match.competition_type}  —  {match.date}")

    y = height - 100

    # SECTION: Lineup
    p.setFont("Helvetica-Bold", 12)
    p.drawString(40, y, "1. Starting Lineup")
    y -= 18
    p.setFont("Helvetica", 10)
    if lineup.exists():
        for player in lineup:
            text = f"{player.player.name}  ({player.position or 'N/A'})"
            p.drawString(50, y, text)
            y -= 14
            if y < 70:
                p.showPage()
                y = height - 40
    else:
        p.drawString(50, y, "No lineup data available.")
        y -= 14

    # SECTION: Attempts at Goal
    y -= 10
    p.setFont("Helvetica-Bold", 12)
    p.drawString(40, y, "2. Attempts at Goal")
    y -= 18
    p.setFont("Helvetica", 10)
    if attempts.exists():
        for a in attempts:
            player_name = a.player.name if a.player else "Unknown"
            assist = a.assist_by.name if a.assist_by else "-"
            pre_assist = a.pre_assist_by.name if a.pre_assist_by else "-"
            text = f"{a.minute}' {a.second}\" — {player_name} — {a.outcome} — Assist: {assist} — Pre-assist: {pre_assist}"
            p.drawString(50, y, text[:120])  # truncate to avoid overflow; adjust as needed
            y -= 12
            if y < 70:
                p.showPage()
                y = height - 40
    else:
        p.drawString(50, y, "No attempts recorded.")
        y -= 14

    # SECTION: Defensive Stats (compact)
    y -= 10
    p.setFont("Helvetica-Bold", 12)
    p.drawString(40, y, "3. Defensive Stats")
    y -= 18
    p.setFont("Helvetica", 10)
    if defensive_stats.exists():
        for s in defensive_stats:
            card = s.card_outcome
            text = f"{s.player.name}: Tackles W/L {s.tackle_won}/{s.tackle_lost}, Duels W/L {s.physical_duel_won}/{s.physical_duel_lost}, Cards: {card}"
            p.drawString(50, y, text[:120])
            y -= 12
            if y < 70:
                p.showPage()
                y = height - 40
    else:
        p.drawString(50, y, "No defensive stats recorded.")
        y -= 14

    # (You can add more sections here: passing summary, GK distributions, substitutions, team summary etc.)

    p.showPage()
    p.save()
    buffer.seek(0)

    filename = f"{our_team.name.replace(' ', '_')}_vs_{opponent.name.replace(' ', '_')}_report.pdf"
    response = HttpResponse(buffer, content_type='application/pdf')
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


######################################################################################

