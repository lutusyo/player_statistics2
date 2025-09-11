from django.shortcuts import render, get_object_or_404
from players_app.models import Player
from matches_app.models import Match
from defensive_app.models import PlayerDefensiveStats
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json



def defensive_summary_view(request, match_id):
    match = get_object_or_404(Match, id=match_id)

    stats = PlayerDefensiveStats.objects.filter(match=match).select_related('player')

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
        ('yellow_card', 'Yellow Card'),
        ('red_card', 'Red Card'),
    ]

    context = {
        'match': match,
        'stats': stats,
        'event_fields': event_fields,
    }
    return render(request, 'defensive_app/defensive_summary.html', context)