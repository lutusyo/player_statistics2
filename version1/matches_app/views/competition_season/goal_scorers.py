from django.shortcuts import get_object_or_404, render
from django.db.models import Count

from version1.tagging_app.models import AttemptToGoal
from version1.matches_app.models import CompetitionSeason


def competition_season_goal_scorers(request, competition_season_id):
    competition_season = get_object_or_404(CompetitionSeason,
        id=competition_season_id, is_active=True,)

    # DATE FILTER
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    # Finished matches only
    finished_matches = competition_season.matches.filter(result_status="FINISHED")

    # Filter by Match kickoff date
    if start_date:
        finished_matches = finished_matches.filter(date__gte=start_date)

    if end_date:
        finished_matches = finished_matches.filter(date__lte=end_date)

    # GOAL EVENTS
    goal_events = AttemptToGoal.objects.filter(
        match__in=finished_matches,
        outcome="On Target Goal",
        is_own_goal=False,
    )

    # GOALS BY PLAYER + TEAM
    goals = (goal_events
        .filter(player__isnull=False)
        .values(
            "player",
            "player__name",
            "team",
            "team__name",
            "team__age_group__name",
        )
        .annotate(
            goals=Count("id")
        )
    )

    # ASSISTS BY PLAYER + TEAM
    assists = (goal_events
        .filter(assist_by__isnull=False)
        .values(
            "assist_by",
            "assist_by__name",
            "team",
            "team__name",
            "team__age_group__name",
        )
        .annotate(
            assists=Count("id")
        )
    )

    # PRE-ASSISTS BY PLAYER + TEAM
    pre_assists = (goal_events
        .filter(pre_assist_by__isnull=False)
        .values(
            "pre_assist_by",
            "pre_assist_by__name",
            "team",
            "team__name",
            "team__age_group__name",
        )
        .annotate(
            pre_assists=Count("id")
        )
    )

    # COMBINE ALL PLAYERS
    players = {}

    # Goals
    for item in goals:
        key = (item["player"], item["team"])

        players[key] = {
            "player": item["player"],
            "player_name": item["player__name"],
            "team": item["team"],
            "team_name": item["team__name"],
            "age_group": item["team__age_group__name"],
            "goals": item["goals"],
            "assists": 0,
            "pre_assists": 0,
        }

    # Assists
    for item in assists:
        key = (item["assist_by"], item["team"])

        if key not in players:
            players[key] = {
                "player": item["assist_by"],
                "player_name": item["assist_by__name"],
                "team": item["team"],
                "team_name": item["team__name"],
                "age_group": item["team__age_group__name"],
                "goals": 0,
                "assists": 0,
                "pre_assists": 0,
            }

        players[key]["assists"] = item["assists"]

    # Pre-assists
    for item in pre_assists:
        key = (item["pre_assist_by"], item["team"])

        if key not in players:
            players[key] = {
                "player": item["pre_assist_by"],
                "player_name": item["pre_assist_by__name"],
                "team": item["team"],
                "team_name": item["team__name"],
                "age_group": item["team__age_group__name"],
                "goals": 0,
                "assists": 0,
                "pre_assists": 0,
            }

        players[key]["pre_assists"] = item["pre_assists"]

    # FINAL PLAYER LIST
    player_statistics = list(players.values())

    # Main order = Goals
    # Then Assists
    # Then Pre-Assists
    # Then Player Name
    player_statistics.sort(
        key=lambda x: (
            -x["goals"],
            -x["assists"],
            -x["pre_assists"],
            x["player_name"],
        )
    )

    context = {
        "competition_season": competition_season,
        "player_statistics": player_statistics,
        "start_date": start_date or "",
        "end_date": end_date or "",
    }

    return render(request,"matches_app/competition_season/competition_season_goal_scorers.html", context,)