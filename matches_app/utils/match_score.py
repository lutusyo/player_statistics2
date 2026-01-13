# matches_app/utils/match_score.py

from django.db import models
from tagging_app.models import AttemptToGoal, OutcomeChoices

def get_match_score(match):
    """
    Returns (home_goals, away_goals) derived from AttemptTo
    """

    home_team = match.home_team
    away_team = match.away_team

    # HOME GOALS
    home_goals = AttemptToGoal.objects.filter(
        match=match
    ).filter(
        models.Q(
            outcome=OutcomeChoices.ON_TARGET_GOAL,
            team=home_team,
            is_own_goal=False
        )
        |
        models.Q(
            is_own_goal=True,
            own_goal_for = home_team
        )
    ).count()

    # AWAY GOALS
    away_goals = AttemptToGoal.objects.filter(
        match=match
    ).filter(
        models.Q(
            outcome=OutcomeChoices.ON_TARGET_GOAL,
            team=away_team,
            is_own_goal=False
        )
        |
        models.Q(
            is_own_goal=True,
            own_goal_for = away_team
        )
    ).count()

    return home_goals, away_goals


