from django.shortcuts import render, get_object_or_404
from players_app.models import Player
from matches_app.models import Match
from defensive_app.models import PlayerDefensiveStats
from lineup_app.models import MatchLineup
from django.utils import timezone


def tagging_panel_view(request, match_id):
    match = get_object_or_404(Match, id=match_id)

    # Get only players currently on the pitch
    lineup_qs = MatchLineup.objects.filter(match=match).select_related("player")

    # Filter players who are on the pitch right now
    players_on_pitch = [
        l.player for l in lineup_qs
        if l.time_in is not None and (l.time_out is None or l.time_out > 90)
    ]

    # Ensure stats exist for each player (Option B)
    for player in players_on_pitch:
        PlayerDefensiveStats.objects.get_or_create(
            match=match,
            player=player,
            defaults={
                'aerial_duel_won': 0,
                'aerial_duel_lost': 0,
                'tackle_won': 0,
                'tackle_lost': 0,
                'physical_duel_won': 0,
                'physical_duel_lost': 0,
                'duel_1v1_won_att': 0,
                'duel_1v1_lost_att': 0,
                'duel_1v1_won_def': 0,
                'duel_1v1_lost_def': 0,
                'foul_committed': 0,
                'foul_won': 0,
                'corner': 0,
                'offside': 0,
                'yellow_card': 0,
                'red_card': 0,
            }
        )

    # Query the stats for rendering
    stats_qs = PlayerDefensiveStats.objects.filter(match=match, player__in=players_on_pitch).select_related('player')
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
    ]

    return render(request, 'defensive_app/tagging_panel.html', {
        'match': match,
        'players': players_on_pitch,
        'stats': stats,
        'events': events,
    })
