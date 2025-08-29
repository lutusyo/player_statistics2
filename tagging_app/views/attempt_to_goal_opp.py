# tagging_app/views.py
from django.shortcuts import render, get_object_or_404
from tagging_app.models import DeliveryTypeChoices, OutcomeChoices, AttemptToGoal
from matches_app.models import Match
from lineup_app.models import MatchLineup
from teams_app.models import Team
from django.views.decorators.csrf import csrf_exempt
import json
import traceback
from django.http import JsonResponse
from tagging_app.utils.attempt_to_goal_utils_opp import get_opponent_goals_for_match



def enter_attempt_to_goal_opp(request, match_id):
    match = get_object_or_404(Match, id=match_id)

    opponent_goals = get_opponent_goals_for_match(match)  # ✅ Use utility function

    context = {
        'match': match,
        'delivery_types': DeliveryTypeChoices.choices,
        'outcomes': OutcomeChoices.choices,
        'opponent_goals': opponent_goals,  # ✅ Add to context
    }

    return render(request, 'tagging_app/attempt_to_goal_enter_data_opp.html', context)




@csrf_exempt
def save_attempt_to_goal_opp(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            match = get_object_or_404(Match, id=data['match_id'])

            # Find opponent team
            all_teams = set(MatchLineup.objects.filter(match=match).values_list('team_id', flat=True))
            our_team = MatchLineup.objects.filter(match=match, player__id=data.get('player_id')).values_list('team_id', flat=True).first()
            opponent_team = Team.objects.exclude(id=our_team).filter(id__in=all_teams).first()

            tag = AttemptToGoal.objects.create(
                match=match,
                team=opponent_team,
                player=None,  # No player linked
                minute=data['minute'],
                second=data['second'],
                outcome=data['outcome'],
                delivery_type=data['delivery_type'],
                is_opponent=True,
                is_own_goal=False,
                timestamp=data['timestamp']
            )

            return JsonResponse({"status": "ok"})

        except Exception as e:
            traceback.print_exc()
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)
