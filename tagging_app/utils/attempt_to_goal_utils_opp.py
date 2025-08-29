from tagging_app.models import AttemptToGoal
from matches_app.models import Match

def get_opponent_goals_for_match(match: Match) -> int:
    """
    Returns the number of opponent goals tagged for the given match.
    Opponent goals are defined as 'On Target Goal' with is_opponent=True.
    """
    return AttemptToGoal.objects.filter(
        match=match,
        is_opponent=True,
        outcome='On Target Goal'
    ).count()
