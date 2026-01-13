from collections import defaultdict
from matches_app.models import Match
from matches_app.utils.match_score import get_match_score
from teams_app.models import Team
from django.utils import timezone  # make sure to import this

def build_league_table(competition_type, season, age_group=None):
    """
    Build league table dynamically from match events (AttemptToGoal).
    Only include matches that have ended.
    """

    matches = Match.objects.filter(
        competition_type=competition_type,
        season=season,
    )

    if age_group:
        matches = matches.filter(age_group=age_group)

    # --- Filter only ended matches ---
    now = timezone.now()
    matches = [m for m in matches if m.end_time and m.end_time <= now]

    table = defaultdict(lambda: {
        "P": 0,
        "W": 0,
        "D": 0,
        "L": 0,
        "GF": 0,
        "GA": 0,
        "GD": 0,
        "Pts": 0,
    })

    for match in matches:
        home = match.home_team
        away = match.away_team

        home_goals, away_goals = get_match_score(match)

        # Played
        table[home]["P"] += 1
        table[away]["P"] += 1

        # Goals
        table[home]["GF"] += home_goals
        table[home]["GA"] += away_goals

        table[away]["GF"] += away_goals
        table[away]["GA"] += home_goals

        # Result & points
        if home_goals > away_goals:
            table[home]["W"] += 1
            table[home]["Pts"] +=3
            table[away]["L"] +=1

        elif home_goals < away_goals:
            table[away]["W"] += 1
            table[away]["Pts"] +=3
            table[home]["L"] +=1

        else:
            table[home]["D"] += 1
            table[away]["D"] += 1
            table[home]["Pts"] += 1
            table[away]["Pts"] += 1

    # Goal Difference 
    for team, stats in table.items():
        stats["GD"] = stats["GF"] - stats["GA"]

    # Sort table (League rules)
    sorted_table = sorted(
        table.items(),
        key=lambda item: (
            item[1]["Pts"],
            item[1]["GD"],
            item[1]["GF"]
        ),
        reverse=True
    )

    return sorted_table
