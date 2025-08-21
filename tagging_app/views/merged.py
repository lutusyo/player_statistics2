# tagging_app/views/merged.py
from django.shortcuts import render, get_object_or_404
from matches_app.models import Match
from players_app.models import Player
from lineup_app.models import MatchLineup
from tagging_app.models import PassEvent, AttemptToGoal
from collections import defaultdict
from django.db.models import Count

def tagging_merged_view(request, match_id):
    match = get_object_or_404(Match, id=match_id)

    # ----- CURRENT ON-FIELD PLAYERS -----
    lineup = MatchLineup.objects.filter(
        match=match, time_in__isnull=False, time_out__isnull=True
    ).select_related('player', 'team').order_by('order', 'player__name')
    players = [entry.player for entry in lineup]

    # ----- ATTEMPT TO GOAL DATA -----
    # Outcome counts per player
    outcome_counts = {}
    for player in players:
        counts = AttemptToGoal.objects.filter(player=player, match=match)\
            .values('outcome')\
            .annotate(count=Count('outcome'))
        outcome_dict = {item['outcome']: item['count'] for item in counts}
        outcome_dict['total'] = sum(outcome_dict.values())
        outcome_counts[player.id] = outcome_dict

    # Total counts for outcomes (all players)
    total_outcome_counts = AttemptToGoal.objects.filter(match=match)\
        .values('outcome')\
        .annotate(count=Count('outcome'))
    total_outcome_dict = {item['outcome']: item['count'] for item in total_outcome_counts}

    # Delivery & outcome choices
    delivery_types = [('foot', 'Foot'), ('head', 'Header'), ('other', 'Other')]
    outcomes = [('goal', 'Goal'), ('miss', 'Miss'), ('saved', 'Saved'), ('blocked', 'Blocked')]

    # ----- PASS NETWORK DATA -----
    # Gather all pass events in match
    player_ids_from = PassEvent.objects.filter(match=match).values_list('from_player_id', flat=True)
    player_ids_to = PassEvent.objects.filter(match=match).values_list('to_player_id', flat=True)
    all_player_ids = set(player_ids_from).union(set(player_ids_to))
    pass_players = Player.objects.filter(id__in=all_player_ids).order_by('name')
    player_names = {p.id: p.name for p in pass_players}

    matrix = defaultdict(lambda: defaultdict(int))
    total_passes = defaultdict(int)
    ball_lost = defaultdict(int)

    passes = PassEvent.objects.filter(match=match)\
        .values('from_player_id', 'to_player_id', 'from_team_id', 'to_team_id')\
        .annotate(count=Count('id'))

    for p in passes:
        from_id = p['from_player_id']
        to_id = p['to_player_id']
        cnt = p['count']
        if to_id:
            matrix[from_id][to_id] = cnt
        total_passes[from_id] += cnt
        if p['from_team_id'] != p['to_team_id']:
            ball_lost[from_id] += cnt

    # ----- CONTEXT -----
    context = {
        'match': match,
        'lineup': lineup,
        'players': players,
        'outcome_counts': outcome_counts,
        'total_outcome_counts': total_outcome_dict,
        'delivery_types': delivery_types,
        'outcomes': outcomes,
        'pass_players': pass_players,
        'player_names': player_names,
        'matrix': matrix,
        'total_passes': total_passes,
        'ball_lost': ball_lost,
    }

    return render(request, 'tagging_app/merged.html', context)
