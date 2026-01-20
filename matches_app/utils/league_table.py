from collections import defaultdict
from datetime import date
from django.utils import timezone

from matches_app.models import Match
from matches_app.utils.match_score import get_match_score


def build_league_table(competition=None, season=None, age_group=None):
    """
    Build league table using ONLY finished matches.
    Uses Python filtering because end_time is a @property.
    """

    matches = Match.objects.filter(season=season)

    if competition:
        matches = matches.filter(competition=competition)

    if age_group:
        matches = matches.filter(age_group=age_group)

    # ✅ FILTER FINISHED MATCHES (Python-level)
    now = timezone.now()
    finished_matches = [
        m for m in matches
        if m.end_time and m.end_time <= now
    ]

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

    for match in finished_matches:
        home = match.home_team
        away = match.away_team

        home_goals, away_goals = get_match_score(match)

        table[home]["P"] += 1
        table[away]["P"] += 1

        table[home]["GF"] += home_goals
        table[home]["GA"] += away_goals
        table[away]["GF"] += away_goals
        table[away]["GA"] += home_goals

        if home_goals > away_goals:
            table[home]["W"] += 1
            table[home]["Pts"] += 3
            table[away]["L"] += 1
        elif away_goals > home_goals:
            table[away]["W"] += 1
            table[away]["Pts"] += 3
            table[home]["L"] += 1
        else:
            table[home]["D"] += 1
            table[away]["D"] += 1
            table[home]["Pts"] += 1
            table[away]["Pts"] += 1

    for team, stats in table.items():
        stats["GD"] = stats["GF"] - stats["GA"]

    return sorted(
        table.items(),
        key=lambda x: (x[1]["Pts"], x[1]["GD"], x[1]["GF"]),
        reverse=True
    )
