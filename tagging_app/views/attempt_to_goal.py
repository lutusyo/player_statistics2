from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from django.http import JsonResponse, HttpResponse, FileResponse
from django.db.models import Count
import traceback, json, csv, io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from lineup_app.models import MatchLineup
from matches_app.models import Match
from players_app.models import Player
from teams_app.models import Team
from tagging_app.models import AttemptToGoal, DeliveryTypeChoices, OutcomeChoices
from tagging_app.utils.attempt_to_goal_utils import get_match_full_context



def enter_attempt_to_goal(request, match_id):
    match = get_object_or_404(Match, id=match_id)

    # Figure out our vs opponent team
    # (replace with your logic if "our_team" is determined differently)
    our_team = match.home_team  
    opponent_team = match.away_team if match.home_team == our_team else match.home_team

    lineup = MatchLineup.objects.filter(
        match=match, time_in__isnull=False, time_out__isnull=True
    ).select_related("player", "team").order_by("order", "player__name")

    players = [entry.player for entry in lineup]

    # Outcome counts per player
    outcome_counts = {}
    for player in players:
        counts = AttemptToGoal.objects.filter(player=player, match=match) \
            .values("outcome").annotate(count=Count("outcome"))
        outcome_dict = {item["outcome"]: item["count"] for item in counts}
        outcome_dict["total"] = sum(outcome_dict.values())
        outcome_counts[player.id] = outcome_dict

    # Total counts for outcomes
    total_outcome_counts = AttemptToGoal.objects.filter(match=match) \
        .values("outcome").annotate(count=Count("outcome"))
    total_outcome_dict = {item["outcome"]: item["count"] for item in total_outcome_counts}

    context = {
        "match": match,
        "lineup": lineup,
        "players": players,
        "delivery_types": DeliveryTypeChoices.choices,
        "outcomes": OutcomeChoices.choices,
        "outcome_counts": outcome_counts,
        "total_outcome_counts": total_outcome_dict,
        "our_team": our_team,
        "opponent_team": opponent_team,
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




from django.db.models import Q

from django.db.models import Count

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

    # ✅ Add goals
    goals = AttemptToGoal.objects.filter(match=match).filter(
        Q(outcome="On Target Goal") | Q(is_own_goal=True)
    ).select_related("player", "assist_by", "pre_assist_by", "team", "own_goal_for").order_by("minute", "second")

    # Update context
    context.update({
        "players": players,
        "outcomes_matrix": outcomes_matrix,
        "goals": goals,
        "match": match,
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
    writer.writerow(['Player', 'Body Part', 'Delivery Type', 'Zone X', 'Zone Y'])

    attempts = AttemptToGoal.objects.filter(match_id=match_id)
    for a in attempts:
        writer.writerow([
            a.player.name if a.player else 'N/A',
            a.delivery_type,
            a.x,
            a.y
        ])
    return response


def export_attempt_to_goal_pdf(request, match_id):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    c.drawString(100, 800, f"Attempt to Goal Report for Match {match_id}")

    attempts = AttemptToGoal.objects.filter(match_id=match_id)
    y = 750
    for a in attempts:
        c.drawString(100, y, f"{a.player.name} | Zone: {a.x}, {a.y}")
        y -= 15
        if y < 50:
            c.showPage()
            y = 800

    c.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='attempt_to_goal.pdf')



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

