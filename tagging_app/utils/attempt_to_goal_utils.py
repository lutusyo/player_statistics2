# tagging_app/utils/attempt_to_goal_utils.py

from collections import defaultdict
from django.shortcuts import get_object_or_404
from tagging_app.models import AttemptToGoal
from matches_app.models import Match
from players_app.models import Player
from django.db.models import Count


def get_attempt_to_goal_context(match_id):
    match = get_object_or_404(Match, id=match_id)

    # Players with attempts
    players = Player.objects.filter(attempts__match=match).distinct()
    player_names = {p.id: p.name for p in players}

    # Matrix of outcomes per player
    outcomes_matrix = defaultdict(lambda: defaultdict(int))
    attempts = AttemptToGoal.objects.filter(match=match)

    for attempt in attempts:
        if attempt.player:
            outcomes_matrix[attempt.player.id][attempt.outcome] += 1

    # Top scorers
    goal_counts = (
        attempts.filter(outcome='On Target Goal')  # Ensure this string matches your model
        .values('player_id')
        .annotate(goals=Count('id'))
    )

    top_scorers = sorted(
        [(player_names[g['player_id']], g['goals']) for g in goal_counts if g['player_id'] in player_names],
        key=lambda x: x[1], reverse=True
    )[:5]

    return {
        'match': match,
        'players': players,
        'outcomes_matrix': outcomes_matrix,
        'top_scorers': top_scorers,
    }
