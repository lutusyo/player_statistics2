from django.shortcuts import render, get_object_or_404
from tagging_app.models import DeliveryTypeChoices, OutcomeChoices, AttemptToGoal
from matches_app.models import Match
from teams_app.models import Team
from django.views.decorators.csrf import csrf_exempt
import json, traceback
from django.http import JsonResponse
from tagging_app.utils.attempt_to_goal_utils_opp import get_opponent_goals_for_match


def enter_attempt_to_goal_opp(request, match_id):
    match = get_object_or_404(Match, id=match_id)

    # Pick opponent relative to our_team
    # (assumes match has home_team & away_team set)
    our_team = match.home_team
    opponent_team = match.away_team if our_team == match.home_team else match.home_team

    opponent_goals = get_opponent_goals_for_match(match, opponent_team)

    context = {
        "match": match,
        "delivery_types": DeliveryTypeChoices.choices,
        "outcomes": OutcomeChoices.choices,
        "opponent_goals": opponent_goals,
        "opponent_team": opponent_team,
    }
    return render(request, "tagging_app/attempt_to_goal_enter_data_opp.html", context)


@csrf_exempt
def save_attempt_to_goal_opp(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body)
        match = get_object_or_404(Match, id=data["match_id"])
        opponent_team = get_object_or_404(Team, id=data["team_id"])

        # Determine if this is an own goal
        is_own_goal = data.get("outcome") == "Own Goal"

        AttemptToGoal.objects.create(
            match=match,
            team=opponent_team,
            player=None,  # opponent tagging doesn’t track players
            minute=data["minute"],
            second=data["second"],
            outcome=data["outcome"],
            delivery_type=data["delivery_type"],
            is_opponent=True,
            is_own_goal=is_own_goal,  # ✅ correctly set
            timestamp=data["timestamp"],
            own_goal_for=match.home_team if is_own_goal else None  # store benefiting team
        )

        return JsonResponse({"status": "ok"})
    except Exception as e:
        import traceback; traceback.print_exc()
        return JsonResponse({"status": "error", "message": str(e)}, status=400)

