from django.shortcuts import render, get_object_or_404
from players_app.models import Player
from matches_app.models import Match
from defensive_app.models import PlayerDefensiveStats
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

@csrf_exempt
def record_event_view(request, match_id):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid method"}, status=405)

    try:
        data = json.loads(request.body)
        player_id = data.get('player_id')        # our player who committed/fouls won
        event = data.get('event')
        card = data.get('card')                  # "yellow", "red", or None
        event_time = data.get('time', timezone.now().isoformat())
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)

    if not player_id or not event:
        return JsonResponse({"status": "error", "message": "Missing player_id or event"}, status=400)

    try:
        stat = PlayerDefensiveStats.objects.get(match_id=match_id, player_id=player_id)
    except PlayerDefensiveStats.DoesNotExist:
        return JsonResponse({"status": "error", "message": "PlayerDefensiveStats not found"}, status=404)

    if not hasattr(stat, event):
        return JsonResponse({"status": "error", "message": "Invalid event"}, status=400)

    # Increment the selected event
    setattr(stat, event, getattr(stat, event) + 1)

    # Handle cards
    match = stat.match  # get the match instance
    if event == "foul_committed":
        if card == "yellow":
            stat.yellow_card += 1
        elif card == "red":
            stat.red_card += 1
    elif event == "foul_won":
        # Card goes to opponent team (team-level fields)
        if card == "yellow":
            match.opponent_yellow_cards = getattr(match, 'opponent_yellow_cards', 0) + 1
        elif card == "red":
            match.opponent_red_cards = getattr(match, 'opponent_red_cards', 0) + 1
        match.save()

    stat.save()

    return JsonResponse({
        "status": "ok",
        "player_id": player_id,
        "event": event,
        "new_value": getattr(stat, event),
        "yellow_card": stat.yellow_card,
        "red_card": stat.red_card,
        "card": card,
        "time": event_time
    })


