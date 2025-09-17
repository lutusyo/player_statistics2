from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json

from defensive_app.models import PlayerDefensiveStats
from matches_app.models import Match
from players_app.models import Player

VALID_EVENTS = [
    "aerial_duel_won", "aerial_duel_lost",
    "tackle_won", "tackle_lost",
    "physical_duel_won", "physical_duel_lost",
    "duel_1v1_won_att", "duel_1v1_lost_att",
    "duel_1v1_won_def", "duel_1v1_lost_def",
    "foul_committed", "foul_won",
    "corner", "offside",
]

@csrf_exempt
def record_event_view(request, match_id):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid method"}, status=405)

    try:
        data = json.loads(request.body)
        player_id = int(data.get('player_id'))
        event = data.get('event')
        card = data.get('card')  # "yellow", "red", or None
        event_time = data.get('time', timezone.now().isoformat())
    except (json.JSONDecodeError, TypeError, ValueError) as e:
        return JsonResponse({"status": "error", "message": f"Invalid JSON or player_id: {str(e)}"}, status=400)

    # Validate event
    if event not in VALID_EVENTS:
        return JsonResponse({"status": "error", "message": f"Invalid event: {event}"}, status=400)

    # Ensure the player and match exist
    player = get_object_or_404(Player, id=player_id)
    match = get_object_or_404(Match, id=match_id)

    # Get or create player stats for this match
    stat, created = PlayerDefensiveStats.objects.get_or_create(match=match, player=player)

    # Increment the event
    current_value = getattr(stat, event, None)
    if current_value is None:
        return JsonResponse({"status": "error", "message": f"Event field missing: {event}"}, status=400)
    setattr(stat, event, current_value + 1)

    # Handle cards if the event is foul_committed
    if event == "foul_committed":
        if card == "yellow":
            stat.yellow_card += 1
        elif card == "red":
            stat.red_card += 1

    stat.save()

    return JsonResponse({
        "status": "ok",
        "player_id": player.id,
        "event": event,
        "new_value": getattr(stat, event),
        "yellow_card": stat.yellow_card,
        "red_card": stat.red_card,
        "card": card,
        "time": event_time
    })
