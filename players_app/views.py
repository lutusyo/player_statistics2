from django.shortcuts import render, get_object_or_404
from django.db.models import Sum, Avg, Count
from django.contrib.auth.decorators import login_required
from collections import defaultdict
from django.http import Http404

from teams_app.models import AgeGroup
from matches_app.models import Match
from lineup_app.models import MatchLineup
from gps_app.models import GPSRecord
from tagging_app.models import AttemptToGoal, PassEvent, GoalkeeperDistributionEvent

#from goalkeeping_app.models import GoalkeeperDistributionEvent
from defensive_app.models import PlayerDefensiveStats
from .models import Player, PlayerCareerStage
from defensive_app.models import  PlayerDefensiveStats


@login_required
def player_list(request):
    age_group_code = request.GET.get('age_group')

    if age_group_code:
        try:
            age_group = AgeGroup.objects.get(code=age_group_code)
            players = Player.objects.filter(age_group=age_group, is_active=True)
        except AgeGroup.DoesNotExist:
            players = Player.objects.none()
    else:
        players = Player.objects.filter(age_group__code='U20', is_active=True)

    # Group players by position
    grouped_players = defaultdict(list)
    for player in players:
        grouped_players[player.position].append(player)

    position_order = ['Goalkeeper', 'Defender', 'Midfielder', 'Forward']

    age_groups = AgeGroup.objects.values_list('code', flat=True)

    return render(request, 'players_app/player_list.html', {
        'grouped_players': grouped_players,
        'position_order': position_order,
        'players': players,
        'age_groups': age_groups,
        'selected_age_group': age_group_code
    })

@login_required
def player_detail(request, player_id):
    player = get_object_or_404(Player, id=player_id)

    # 🔒 Prevent showing detail of inactive player
    if not player.is_active:
        raise Http404("This player is inactive")

    # Only show active related players
    related_players = Player.objects.filter(
        age_group=player.age_group,
        is_active=True
    ).exclude(id=player_id)

    stages = player.career_stages.all()
    selected_age_group = request.GET.get('age_group')

    context = {
        'player': player,
        'related_players': related_players,
        'stages': stages,
        'selected_age_group': selected_age_group,
    }
    return render(request, 'players_app/player_detail.html', context)



def player_match_detail(request, player_id, match_id):
    player = get_object_or_404(Player, id=player_id)
    player_matches = Match.objects.filter(gps_records__player=player).distinct().order_by('-date')

    if str(match_id) == 'total':
        gps_agg = GPSRecord.objects.filter(player=player).aggregate(
            total_distance=Sum('distance'),
            avg_max_velocity=Avg('max_velocity'),
            total_sprint_distance=Sum('sprint_distance'),
            total_player_load=Sum('player_load'),
        )
        attempts_outcomes = AttemptToGoal.objects.filter(player=player).values('outcome').annotate(count=Count('outcome'))
        outcome_labels = [a['outcome'] for a in attempts_outcomes]
        outcome_counts = [a['count'] for a in attempts_outcomes]

        defensive_stats_agg = PlayerDefensiveStats.objects.filter(player=player).aggregate(
            total_aerial_won=Sum('aerial_duel_won'),
            total_aerial_lost=Sum('aerial_duel_lost'),
            total_tackle_won=Sum('tackle_won'),
            total_tackle_lost=Sum('tackle_lost'),
            total_physical_won=Sum('physical_duel_won'),
            total_physical_lost=Sum('physical_duel_lost'),
        )

        # Get GPS summary per match for table rows
        gps_per_match = (
            GPSRecord.objects.filter(player=player)
            .values('match__id', 'match__date', 'match__home_team__name', 'match__away_team__name')
            .annotate(
                total_distance=Sum('distance'),
                avg_max_velocity=Avg('max_velocity'),
                total_sprint_distance=Sum('sprint_distance'),
                total_player_load=Sum('player_load'),
            )
            .order_by('-match__date')
        )

        context = {
            'player': player,
            'player_matches': player_matches,
            'selected_match': None,
            'gps_agg': gps_agg,
            'outcome_labels': outcome_labels,
            'outcome_counts': outcome_counts,
            'defensive_stats_agg': defensive_stats_agg,
            'gps_per_match': gps_per_match,
        }

    else:
        # specific match id
        match = get_object_or_404(Match, id=match_id)

        gps_records = GPSRecord.objects.filter(player=player, match=match)
        attempts = AttemptToGoal.objects.filter(player=player, match=match)
        passes_made = PassEvent.objects.filter(from_player=player, match=match)
        passes_received = PassEvent.objects.filter(to_player=player, match=match)
        gk_distributions = GoalkeeperDistributionEvent.objects.filter(goalkeeper=player, match=match)
        defensive_stats = PlayerDefensiveStats.objects.filter(player=player, match=match).first()

        attempts_outcomes = attempts.values('outcome').annotate(count=Count('outcome'))
        outcome_labels = [a['outcome'] for a in attempts_outcomes]
        outcome_counts = [a['count'] for a in attempts_outcomes]

        defensive_duels = {
            'Aerial Duel Won': defensive_stats.aerial_duel_won if defensive_stats else 0,
            'Aerial Duel Lost': defensive_stats.aerial_duel_lost if defensive_stats else 0,
            'Tackle Won': defensive_stats.tackle_won if defensive_stats else 0,
            'Tackle Lost': defensive_stats.tackle_lost if defensive_stats else 0,
        }

        defensive_duels_keys = list(defensive_duels.keys())
        defensive_duels_values = list(defensive_duels.values())

        context = {
            'player': player,
            'player_matches': player_matches,
            'selected_match': match,
            'gps_records': gps_records,
            'attempts': attempts,
            'passes_made': passes_made,
            'passes_received': passes_received,
            'gk_distributions': gk_distributions,
            'defensive_stats': defensive_stats,
            'defensive_duels': defensive_duels,
            'defensive_duels_keys': defensive_duels_keys,
            'defensive_duels_values': defensive_duels_values,
            'outcome_labels': outcome_labels,
            'outcome_counts': outcome_counts,
        }

    return render(request, 'players_app/player_match_detail.html', context)



