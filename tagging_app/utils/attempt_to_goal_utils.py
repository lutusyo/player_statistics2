from collections import defaultdict
from django.shortcuts import get_object_or_404
from tagging_app.models import AttemptToGoal
from matches_app.models import Match
from players_app.models import Player
from django.db.models import Count


def get_attempt_to_goal_context(match_id):
    match = get_object_or_404(Match, id=match_id)

    # Identify teams from AttemptToGoal records
    our_attempt = AttemptToGoal.objects.filter(match=match, is_opponent=False).first()
    opponent_attempt = AttemptToGoal.objects.filter(match=match, is_opponent=True).first()

    our_team = our_attempt.team if our_attempt else match.home_team  # fallback to home_team
    opponent_team = opponent_attempt.team if opponent_attempt else match.away_team

    # 1. OUR TEAM'S ATTEMPTS
    our_team_attempts = AttemptToGoal.objects.filter(
        match=match,
        is_opponent=False
    )

    # 2. OPPONENT'S ATTEMPTS
    opponent_attempts = AttemptToGoal.objects.filter(
        match=match,
        is_opponent=True
    )

    # 3. OPPONENT GOALS ONLY
    opponent_goals = opponent_attempts.filter(outcome='On Target Goal')

    # 4. Players from our team who made attempts
    players = Player.objects.filter(attempts__in=our_team_attempts).distinct()
    player_names = {p.id: p.name for p in players}

    # 5. Outcomes matrix (per player)
    outcomes_matrix = defaultdict(lambda: defaultdict(int))
    for attempt in our_team_attempts:
        if attempt.player:
            outcomes_matrix[attempt.player.id][attempt.outcome] += 1

    # 6. Top scorers (our team only)
    goal_counts = (
        our_team_attempts.filter(outcome='On Target Goal', is_own_goal=False)
        .values('player_id')
        .annotate(goals=Count('id'))
    )

    top_scorers = sorted(
        [(player_names[g['player_id']], g['goals']) for g in goal_counts if g['player_id'] in player_names],
        key=lambda x: x[1],
        reverse=True
    )[:5]

    return {
        'match': match,
        'our_team': our_team,
        'opponent_team': opponent_team,
        'players': players,
        'outcomes_matrix': outcomes_matrix,
        'top_scorers': top_scorers,
        'opponent_goals': opponent_goals,
        'our_team_attempts': our_team_attempts,
        'opponent_attempts': opponent_attempts,
    }
