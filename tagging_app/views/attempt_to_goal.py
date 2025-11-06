from io import BytesIO
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse, HttpResponse
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
from tagging_app.models import AttemptToGoal, DeliveryTypeChoices, OutcomeChoices, BodyPartChoices, LocationChoices
from tagging_app.utils.attempt_to_goal_utils import get_match_full_context
import json
import traceback

# tagging_app/views/pass_network.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt

from collections import defaultdict
import csv
import io
import json

from django.db.models import Count
from players_app.models import Player
from matches_app.models import Match
from lineup_app.models import MatchLineup
from tagging_app.models import PassEvent
from teams_app.models import Team

# ReportLab (PDF)
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Image, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# Excel
from openpyxl import Workbook

# Matplotlib (server-side)
import matplotlib
matplotlib.use('Agg')  # non-GUI backend for servers
import matplotlib.pyplot as plt
# tagging_app/views/pass_network.py
from django.shortcuts import render, get_object_or_404
from tagging_app.utils.pass_network_utils import get_pass_network_context  # ✅ add this





def enter_attempt_to_goal(request, match_id):
    match = get_object_or_404(Match, id=match_id)

    # Determine which team is active
    selected_team_id = request.GET.get("team_id")

    # Default to home team if none selected
    if selected_team_id:
        active_team = get_object_or_404(Team, id=selected_team_id)
    else:
        active_team = match.home_team

    # Identify opponent correctly
    if active_team == match.home_team:
        opponent_team = match.away_team
    else:
        opponent_team = match.home_team

    # ✅ Get the correct lineup (based on active_team)
    lineup = (
        MatchLineup.objects.filter(match=match, team=active_team)
        .select_related("player", "team")
        .order_by("order", "player__name")
    )

    players = [entry.player for entry in lineup]


    # Outcome counts per player
    outcome_counts = {}
    for player in players:
        counts = AttemptToGoal.objects.filter(player=player, match=match).values("outcome").annotate(count=Count("outcome"))
        outcome_dict = {item["outcome"]: item["count"] for item in counts}
        outcome_dict["total"] = sum(outcome_dict.values())
        outcome_counts[player.id] = outcome_dict

    # Total outcome counts
    total_outcome_counts = (
        AttemptToGoal.objects.filter(match=match, team=active_team)
        .values("outcome")
        .annotate(count=Count("outcome"))
    )
    total_outcome_dict = {item["outcome"]: item["count"] for item in total_outcome_counts}

    context = {
        "match": match,
        "players": players,
        "delivery_types": DeliveryTypeChoices.choices,
        "outcomes": OutcomeChoices.choices,
        "body_parts": BodyPartChoices.choices,
        "locations": LocationChoices.choices,
        "outcome_counts": outcome_counts,
        "total_outcome_counts": total_outcome_dict,
        "active_team": active_team,
        "opponent_team": opponent_team,
        "home_team": match.home_team,
        "away_team": match.away_team,
    }

    return render(request, "tagging_app/attempt_to_goal_enter_data.html", context)







@csrf_exempt
def save_attempt_to_goal(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body)
        match = get_object_or_404(Match, id=data["match_id"])

        player = Player.objects.filter(id=data.get("player_id")).first()
        team = get_object_or_404(Team, id=data["team_id"])

        # Own goal
        is_own_goal = data.get("is_own_goal", False)
        own_goal_for = Team.objects.filter(id=data.get("own_goal_for_id")).first()

        AttemptToGoal.objects.create(
            match=match,
            player=player,
            team=team,
            outcome=data["outcome"],
            delivery_type=data["delivery_type"],
            body_part = data.get("body_part"),

            location_tag = data.get("location_tag"),
            assist_by_id=data.get("assist_by_id"),
            
            pre_assist_by_id=data.get("pre_assist_by_id"),
            minute=data["minute"],
            second=data["second"],
            is_own_goal=is_own_goal,
            own_goal_for=own_goal_for,
            is_opponent=data.get("is_opponent", False),
            timestamp=data.get("timestamp"),
        )

        # Return updated outcome counts for this team
        outcome_counts = (
            AttemptToGoal.objects.filter(match=match, team=team)
            .values("outcome")
            .annotate(count=Count("outcome"))
        )
        outcome_dict = {row["outcome"]: row["count"] for row in outcome_counts}
        outcome_dict["total"] = sum(outcome_dict.values())

        return JsonResponse({"status": "ok", "updated_counts": outcome_dict})

    except Exception as e:
        traceback.print_exc()
        return JsonResponse({"status": "error", "message": str(e)}, status=400)
    



















def attempt_to_goal_dashboard(request, match_id):
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

    return render(request, "tagging_app/attempt_to_goal_dashboard.html", context)






















def goals_list(request, match_id):
    match = get_object_or_404(Match, id=match_id)

    # Goals = On Target Goal OR Own Goal
    goals = AttemptToGoal.objects.filter(
        match=match
    ).filter(
        Q(outcome="On Target Goal") | Q(is_own_goal=True)
    ).select_related(
        "player", "assist_by", "pre_assist_by", "team", "own_goal_for"
    ).order_by("minute", "second")

    context = {
        "match": match,
        "goals": goals,
    }
    return render(request, "tagging_app/goals_list.html", context)




@require_GET
def get_live_tagging_state(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    attempts = AttemptToGoal.objects.filter(match=match).order_by('-timestamp')[:20]
    data = [{
        'player_name': a.player.name,
        'outcome': a.outcome,
        'delivery_type': a.delivery_type,
        'minute': a.minute,
        'second': a.second
    } for a in reversed(attempts)]  # oldest first
    return JsonResponse({
        'timer': 0,  # You can later add a MatchTimer model here
        'events': data
    })


def export_attempt_to_goal_csv(request, match_id):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="attempt_to_goal_{match_id}.csv"'
    writer = csv.writer(response)
    writer.writerow(['Player', 'Body Part', 'Delivery Type', 'Location', 'Zone X', 'Zone Y'])

    attempts = AttemptToGoal.objects.filter(match_id=match_id)
    for a in attempts:
        writer.writerow([
            a.player.name if a.player else 'N/A',
            a.get_body_part_display(),
            a.get_delivery_type_display(),
            a.get_location_tag_display(),
            a.x,
            a.y
        ])
    return response





def link_callback(uri, rel):
    """
    Convert URIs to absolute system paths for xhtml2pdf.
    Handles both STATIC and MEDIA files safely.
    """
    result = finders.find(uri)
    if result:
        if isinstance(result, (list, tuple)):
            result = result[0]
        return os.path.realpath(result)

    sUrl = settings.STATIC_URL
    mUrl = settings.MEDIA_URL
    mRoot = settings.MEDIA_ROOT

    if uri.startswith(mUrl):
        path = os.path.join(mRoot, uri.replace(mUrl, ""))
    elif uri.startswith(sUrl):
        for static_dir in settings.STATICFILES_DIRS:
            candidate = os.path.join(static_dir, uri.replace(sUrl, ""))
            if os.path.isfile(candidate):
                return os.path.realpath(candidate)
        if settings.STATIC_ROOT:
            candidate = os.path.join(settings.STATIC_ROOT, uri.replace(sUrl, ""))
            if os.path.isfile(candidate):
                return os.path.realpath(candidate)
        raise FileNotFoundError(f"Static file not found: {uri}")
    else:
        return uri

    if not os.path.isfile(path):
        raise FileNotFoundError(f"Cannot find file: {uri}")

    return os.path.realpath(path)




def download_attempt_to_goal_pdf(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    our_attempts = AttemptToGoal.objects.filter(match=match, is_opponent=False)

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=20, leftMargin=20,
                            topMargin=20, bottomMargin=20)

    styles = getSampleStyleSheet()
    styleH = styles['Heading2']

    elements = []

    # Title
    elements.append(Paragraph(f"{match.home_team.name} - Attempts to Goal Dashboard", styleH))
    elements.append(Spacer(1, 12))

    # Summary Table
    summary_data = [["Outcome", "Shots"]]
    summary_data += [
        ["Goals", our_attempts.filter(outcome='GOAL').count()],
        ["On Target", our_attempts.filter(outcome='ON_TARGET_GOAL').count()],
        ["Off Target", our_attempts.filter(outcome='OFF_TARGET').count()],
        ["Blocked", our_attempts.filter(outcome='BLOCKED').count()],
        ["Incomplete/Errors", our_attempts.filter(outcome='PLAYER_ERROR').count()],
    ]

    table = Table(summary_data, hAlign='LEFT', colWidths=[150, 80])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.black),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 20))

    # Detailed Attempts Table
    elements.append(Paragraph("Detailed Goal Attempts", styleH))
    elements.append(Spacer(1, 12))

    attempt_data = [["Time", "Player", "Outcome", "Body Part", "Delivery Type", "Location"]]
    for attempt in our_attempts:
        attempt_data.append([
            f"{attempt.minute}:{str(attempt.second).zfill(2)}",
            attempt.player.name,
            attempt.outcome,
            attempt.get_body_part_display(),
            attempt.get_delivery_type_display(),
            attempt.get_location_tag_display(),
        ])

    attempts_table = Table(attempt_data, hAlign='LEFT', colWidths=[50, 100, 80, 80, 80, 80])
    attempts_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(attempts_table)

    doc.build(elements)

    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="attempt_to_goal_{match_id}.pdf"'
    return response






@require_GET
def get_outcome_counts(request, match_id):
    """Return total counts of each outcome for a match (all players)."""
    match = get_object_or_404(Match, id=match_id)

    outcome_counts = (
        AttemptToGoal.objects.filter(match=match)
        .values('outcome')
        .annotate(count=Count('id'))
    )
    counts_dict = {row['outcome']: row['count'] for row in outcome_counts}

    return JsonResponse(counts_dict)

#####################################################################################################################################






# ---------- SHARED DATA FUNCTION ----------
def get_pass_network_data(match_id):
    """
    Returns:
        players: QuerySet of Player (ordered by name)
        player_names: dict {player_id: player_name}
        matrix: dict[from_id][to_id] = count
        total_passes: dict[from_id] = total passes made
        ball_lost: dict[from_id] = passes that changed team away from passer's team
    """

    match = get_object_or_404(Match, id=match_id)
    player_ids_from = PassEvent.objects.filter(match=match).values_list('from_player_id', flat=True)
    player_ids_to = PassEvent.objects.filter(match=match).values_list('to_player_id', flat=True)
    all_player_ids = set(player_ids_from).union(set(player_ids_to))

    players = Player.objects.filter(id__in=all_player_ids).order_by('name')
    player_names = {p.id: p.name for p in players}

    # Build counts
    matrix = defaultdict(lambda: defaultdict(int))
    passes = (
        PassEvent.objects.filter(match=match)
        .values('from_player_id', 'to_player_id', 'from_team_id', 'to_team_id')
        .annotate(count=Count('id'))
    )

    total_passes = defaultdict(int)
    ball_lost = defaultdict(int)

    for p in passes:
        from_id = p['from_player_id']
        to_id = p['to_player_id']
        cnt = p['count']

        if to_id:
            matrix[from_id][to_id] = cnt
        total_passes[from_id] += cnt
        if p['from_team_id'] != p['to_team_id']:
            ball_lost[from_id] += cnt

    return players, player_names, matrix, total_passes, ball_lost

def pass_network_dashboard(request, match_id):
    match = get_object_or_404(Match, id=match_id)  # ✅ Add this line
    context = get_pass_network_context(match)      # ✅ Use the Match object, not match_id
    context['match'] = match                       # ✅ Add match to context explicitly
    return render(request, 'tagging_app/pass_network_dashboard.html', context)
    #return render(request, 'tagging_app/attempt_to_goal_dashboard.html', context)













    
