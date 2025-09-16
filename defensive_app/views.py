from django.shortcuts import render, get_object_or_404
from players_app.models import Player
from matches_app.models import Match
from .models import PlayerDefensiveStats
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from django.shortcuts import render, get_object_or_404
from players_app.models import Player
from matches_app.models import Match
from .models import PlayerDefensiveStats


def tagging_panel(request, match_id):
    match = get_object_or_404(Match, id=match_id)

    # Get lineup players — filter as needed
    players = Player.objects.all()

    # Ensure PlayerDefensiveStats exists for each player in match
    for player in players:
        PlayerDefensiveStats.objects.get_or_create(match=match, player=player)

    # Query all defensive stats for this match
    stats_qs = PlayerDefensiveStats.objects.filter(match=match).select_related('player')

    # Build dictionary: {player_id: PlayerDefensiveStats instance}
    stats = {stat.player.id: stat for stat in stats_qs}

    events = [
        ("aerial_duel_won", "Aerial Duel Won"),
        ("aerial_duel_lost", "Aerial Duel Lost"),
        ("tackle_won", "Tackle Won"),
        ("tackle_lost", "Tackle Lost"),
        ("physical_duel_won", "Physical Duel Won"),
        ("physical_duel_lost", "Physical Duel Lost"),
        ("duel_1v1_won_att", "1v1 Attack Won"),
        ("duel_1v1_lost_att", "1v1 Attack Lost"),
        ("duel_1v1_won_def", "1v1 Defense Won"),
        ("duel_1v1_lost_def", "1v1 Defense Lost"),
        ("foul_committed", "Foul Committed"),
        ("foul_won", "Foul Won"),
        ("corner", "Corner"),
        ("offside", "Offside"),
        ("yellow_card", "Yellow Card"),
        ("red_card", "Red Card"),
    ]

    return render(request, 'defensive_app/tagging_panel.html', {
        'match': match,
        'players': players,
        'stats': stats,  # dictionary instead of queryset
        'events': events,
    })


@csrf_exempt
def record_event(request, match_id):
    if request.method == "POST":
        data = json.loads(request.body)
        player_id = data.get('player_id')
        event = data.get('event')
        card = data.get('card')  # NEW: read card selection

        if not player_id or not event:
            return JsonResponse({"status": "error", "message": "Missing player_id or event"}, status=400)

        try:
            stat = PlayerDefensiveStats.objects.get(match_id=match_id, player_id=player_id)
        except PlayerDefensiveStats.DoesNotExist:
            return JsonResponse({"status": "error", "message": "PlayerDefensiveStats not found"}, status=404)

        # Update the numeric event
        if hasattr(stat, event):
            current_value = getattr(stat, event)
            setattr(stat, event, current_value + 1)

        # Update card if applicable
        if card == "yellow":
            stat.yellow_card = 1
        elif card == "red":
            stat.red_card = 1

        stat.save()
        return JsonResponse({
            "status": "ok",
            "new_value": getattr(stat, event),
            "player_id": player_id,
            "event": event,
            "card": card
        })

    return JsonResponse({"status": "error", "message": "Invalid method"}, status=405)




def defensive_summary(request, match_id):
    match = get_object_or_404(Match, id=match_id)

    # Ensure all players have defensive stats for this match
    players = Player.objects.all()
    for player in players:
        PlayerDefensiveStats.objects.get_or_create(match=match, player=player)

    # Fetch all stats
    stats_qs = PlayerDefensiveStats.objects.filter(match=match).select_related('player')

    # Prepare data for template
    players_stats = []
    for stat in stats_qs:
        if stat.red_card > 0:
            card_outcome = "RED CARD"
        elif stat.yellow_card > 0:
            card_outcome = "YELLOW CARD"
        else:
            card_outcome = "NO CARD"

        players_stats.append({
            'player': stat.player,
            'foul_committed': stat.foul_committed,
            'foul_won': stat.foul_won,
            'card_outcome': card_outcome,
            'aerial_duel_won': stat.aerial_duel_won,
            'aerial_duel_lost': stat.aerial_duel_lost,
            'tackle_won': stat.tackle_won,
            'tackle_lost': stat.tackle_lost,
            'physical_duel_won': stat.physical_duel_won,
            'physical_duel_lost': stat.physical_duel_lost,
            'duel_1v1_won_att': stat.duel_1v1_won_att,
            'duel_1v1_lost_att': stat.duel_1v1_lost_att,
            'duel_1v1_won_def': stat.duel_1v1_won_def,
            'duel_1v1_lost_def': stat.duel_1v1_lost_def,
            'corner': stat.corner,
            'offside': stat.offside,
        })

    # Define fields for full table
    event_fields = [
        ('aerial_duel_won', 'Aerial Duel Won'),
        ('aerial_duel_lost', 'Aerial Duel Lost'),
        ('tackle_won', 'Tackle Won'),
        ('tackle_lost', 'Tackle Lost'),
        ('physical_duel_won', 'Physical Duel Won'),
        ('physical_duel_lost', 'Physical Duel Lost'),
        ('duel_1v1_won_att', '1v1 Duel Won (Att)'),
        ('duel_1v1_lost_att', '1v1 Duel Lost (Att)'),
        ('duel_1v1_won_def', '1v1 Duel Won (Def)'),
        ('duel_1v1_lost_def', '1v1 Duel Lost (Def)'),
        ('foul_committed', 'Foul Committed'),
        ('foul_won', 'Foul Won'),
        ('corner', 'Corner'),
        ('offside', 'Offside'),
    ]

    return render(request, 'defensive_app/defensive_summary.html', {
        'match': match,
        'players_stats': players_stats,
        'event_fields': event_fields,
    })



