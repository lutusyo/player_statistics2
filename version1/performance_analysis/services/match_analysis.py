
from django.db.models import Q

from version1.matches_app.models import Match
from .player_minutes import calculate_team_player_minutes



def get_period_teams(analysis, period):
    """Return the teams selected for a reporting period."""

    if analysis.comparison_mode == "SAME_TEAMS":
        return list(
            analysis.selected_teams
            .select_related("team")
            .values_list("team_id", flat=True)
        )

    return list(
        period.selected_teams.values_list("team_id", flat=True)
    )


def get_finished_matches(period, team_ids):
    """Get finished matches involving the selected teams."""

    if not team_ids:
        return Match.objects.none()

    return (
        Match.objects
        .filter(
            date__range=(period.start_date, period.end_date),
            result_status="FINISHED",
        )
        .filter(
            Q(home_team_id__in=team_ids) |
            Q(away_team_id__in=team_ids)
        )
        .select_related("home_team", "away_team")
        .order_by("date")
    )


def calculate_team_results(team, matches):
    """Calculate match results from one team's perspective."""

    stats = {
        "team_id": team.id,
        "team_name": team.name,
        "played": 0,
        "won": 0,
        "drawn": 0,
        "lost": 0,
        "goals_for": 0,
        "goals_against": 0,
        "goal_difference": 0,
        "points": 0,
        "win_percentage": 0,
    }

    for match in matches:
        if match.home_team_id == team.id:
            goals_for = match.home_score
            goals_against = match.away_score
        elif match.away_team_id == team.id:
            goals_for = match.away_score
            goals_against = match.home_score
        else:
            continue

        stats["played"] += 1
        stats["goals_for"] += goals_for
        stats["goals_against"] += goals_against

        if goals_for > goals_against:
            stats["won"] += 1
            stats["points"] += 3
        elif goals_for == goals_against:
            stats["drawn"] += 1
            stats["points"] += 1
        else:
            stats["lost"] += 1

    stats["goal_difference"] = (
        stats["goals_for"] - stats["goals_against"]
    )

    if stats["played"]:
        stats["win_percentage"] = round(
            stats["won"] / stats["played"] * 100, 1
        )

    return stats


def generate_team_match_analysis(analysis):
    """Generate match-result statistics for every period."""

    from version1.teams_app.models import Team

    results = []

    periods = analysis.periods.prefetch_related("selected_teams")

    for period in periods:
        team_ids = get_period_teams(analysis, period)

        teams = Team.objects.filter(
            id__in=team_ids
        ).select_related("age_group")

        matches = list(
            get_finished_matches(period, team_ids)
        )
        match_ids = [match.id for match in matches]



        for team in teams:
                    age_group_value = None
                    if team.age_group:
                        age_group_value = getattr(team.age_group, "name", str(team.age_group))

                    results.append({
                        "period_id": period.id,
                        "period_name": period.name,
                        "start_date": period.start_date.isoformat(),
                        "end_date": period.end_date.isoformat(),
                        "age_group": age_group_value,
                        **calculate_team_results(team, matches),
                        **calculate_team_player_minutes(team, match_ids),
                    })

    return results
