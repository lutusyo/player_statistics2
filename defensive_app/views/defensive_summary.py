from django.shortcuts import render, get_object_or_404
from players_app.models import Player
from matches_app.models import Match
from defensive_app.models import PlayerDefensiveStats
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from django.utils import timezone




def defensive_summary_view(request, match_id):
    match = get_object_or_404(Match, id=match_id)

    players_stats = (
        PlayerDefensiveStats.objects
        .filter(match=match)
        .select_related('player')
    )

    # ✅ Only key defensive event fields
    event_fields = [
        ('aerial_duel_won', 'Aerial Duel Won'),
        ('aerial_duel_lost', 'Aerial Duel Lost'),
        ('tackle_won', 'Tackle Won'),
        ('tackle_lost', 'Tackle Lost'),
        ('duel_1v1_won_att', '1v1 Duel Won (Att)'),
        ('duel_1v1_lost_att', '1v1 Duel Lost (Att)'),
        ('duel_1v1_won_def', '1v1 Duel Won (Def)'),
        ('duel_1v1_lost_def', '1v1 Duel Lost (Def)'),
        ('interception', 'Interceptions'),
        ('ball_recovery', 'Ball Recoveries'),
        ('clearance', 'Clearances'),
        ('foul_committed', 'Foul Committed'),
        ('foul_won', 'Foul Won'),
        ('yellow_card', 'Yellow Card'),
        ('red_card', 'Red Card'),
    ]

    context = {
        'match': match,
        'players_stats': players_stats,
        'event_fields': event_fields,
    }
    return render(request, 'defensive_app/defensive_summary.html', context)

