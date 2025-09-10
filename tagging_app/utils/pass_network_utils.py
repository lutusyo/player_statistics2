from collections import defaultdict
from django.shortcuts import get_object_or_404
from django.db.models import Count
from players_app.models import Player
from matches_app.models import Match
from tagging_app.models import PassEvent

def get_pass_network_context(match_input):
    if isinstance(match_input, Match):
        match = match_input
    else:
        match = get_object_or_404(Match, id=match_input)

    player_ids_from = PassEvent.objects.filter(match=match).values_list('from_player_id', flat=True)
    player_ids_to = PassEvent.objects.filter(match=match).values_list('to_player_id', flat=True)
    all_player_ids = set(player_ids_from).union(set(player_ids_to))

    players = Player.objects.filter(id__in=all_player_ids).order_by('name')
    player_names = {p.id: p.name for p in players}

    matrix = defaultdict(lambda: defaultdict(int))
    passes = (
        PassEvent.objects.filter(match=match)
        .values('from_player_id', 'to_player_id', 'from_team_id', 'to_team_id')
        .annotate(count=Count('id'))
    )

    total_passes = defaultdict(int)
    ball_lost = defaultdict(int)

    for p in passes:
        from_id = p['from_player_id']
        to_id = p['to_player_id']
        cnt = p['count']

        if to_id:
            matrix[from_id][to_id] = cnt
        total_passes[from_id] += cnt
        if p['from_team_id'] != p['to_team_id']:
            ball_lost[from_id] += cnt

    # Top 5 combinations
    combos = []
    for f_id, tos in matrix.items():
        for t_id, c in tos.items():
            combos.append((
                player_names.get(f_id, f"Unknown({f_id})"),
                player_names.get(t_id, f"Unknown({t_id})"),
                c
            ))
    top_combinations = sorted(combos, key=lambda x: x[2], reverse=True)[:5]

    # Chart Data
    chart_data = {
        'names': [player_names[p.id] for p in players],
        'values': [total_passes[p.id] for p in players]
    }

    return {
        'players': players,
        'matrix': matrix,
        'player_names': player_names,
        'top_combinations': top_combinations,
        'total_passes': total_passes,
        'ball_lost': ball_lost,
        'chart_data': chart_data,
    }
