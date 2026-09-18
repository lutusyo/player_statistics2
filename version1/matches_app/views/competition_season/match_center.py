from django.shortcuts import get_object_or_404, render
from version1.tagging_app.models import AttemptToGoal
from version1.matches_app.models import Match


def competition_match_centre(request, match_id):
    match = get_object_or_404(
        Match.objects.select_related(
            "home_team",
            "away_team",
            "venue",
            "competition_season",
            "competition",
        ),
        id=match_id,
    )

    attempts = (
        AttemptToGoal.objects
        .filter(match=match)
        .select_related(
            "player",
            "team",
            "assist_by",
            "pre_assist_by",
            "own_goal_for",
        )
        .order_by("minute", "second")
    )

    # ---------------------------------------------------------
    # HOME TEAM STATISTICS
    # ---------------------------------------------------------

    home_attempts = attempts.filter(team=match.home_team)

    home_shots = home_attempts.count()

    home_shots_on_target = home_attempts.filter(
        outcome__in=[
            "On Target Saved",
            "On Target Goal",
        ]
    ).count()

    home_goals = home_attempts.filter(
        outcome="On Target Goal"
    ).count()

    home_assists = home_attempts.filter(
        assist_by__isnull=False,
        outcome="On Target Goal",
    ).count()

    # ---------------------------------------------------------
    # AWAY TEAM STATISTICS
    # ---------------------------------------------------------

    away_attempts = attempts.filter(team=match.away_team)

    away_shots = away_attempts.count()

    away_shots_on_target = away_attempts.filter(
        outcome__in=[
            "On Target Saved",
            "On Target Goal",
        ]
    ).count()

    away_goals = away_attempts.filter(
        outcome="On Target Goal"
    ).count()

    away_assists = away_attempts.filter(
        assist_by__isnull=False,
        outcome="On Target Goal",
    ).count()

    # ---------------------------------------------------------
    # TEAM STATISTICS
    # ---------------------------------------------------------

    home_stats = {
        "shots": home_shots,
        "shots_on_target": home_shots_on_target,
        "goals": home_goals,
        "assists": home_assists,
    }

    away_stats = {
        "shots": away_shots,
        "shots_on_target": away_shots_on_target,
        "goals": away_goals,
        "assists": away_assists,
    }

    # GOALS
    goals = attempts.filter(outcome="On Target Goal").order_by("minute", "second")

    context = {
        "match": match,
        "attempts": attempts,
        "goals": goals,
        "home_stats": home_stats,
        "away_stats": away_stats,
    }

    return render(request, "matches_app/competition_season/competition_match_centre.html", context,)