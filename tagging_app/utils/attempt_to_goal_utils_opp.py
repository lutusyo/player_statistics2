from tagging_app.models import AttemptToGoal
from matches_app.models import Match, Team

def get_opponent_goals_for_match(match: Match, opponent_team: Team) -> int:
    """
    Returns total goals scored by the opponent team:
    - Normal goals (On Target Goal, is_opponent=True)
    - Own goals that count for opponent (own_goal_for=opponent_team)
    """
    return (
        AttemptToGoal.objects.filter(
            match=match,
            is_opponent=True,
            outcome="On Target Goal",
            team=opponent_team
        ).count()
        + AttemptToGoal.objects.filter(
            match=match,
            is_own_goal=True,
            own_goal_for=opponent_team
        ).count()
    )
