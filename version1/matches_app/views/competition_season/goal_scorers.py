
from django.shortcuts import get_object_or_404, render
from django.db.models import Count

from version1.tagging_app.models import AttemptToGoal
from version1.matches_app.models import CompetitionSeason

from django.core.files.storage import default_storage


def competition_season_goal_scorers(request, competition_season_id):
    competition_season = get_object_or_404(
        CompetitionSeason,
        id=competition_season_id,
        is_active=True,
    )

    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    # Finished matches only
    finished_matches = competition_season.matches.filter(
        result_status="FINISHED"
    )

    if start_date:
        finished_matches = finished_matches.filter(date__gte=start_date)

    if end_date:
        finished_matches = finished_matches.filter(date__lte=end_date)

    # Goal events
    goal_events = AttemptToGoal.objects.filter(
        match__in=finished_matches,
        outcome="On Target Goal",
        is_own_goal=False,
    )

    # Common player fields
    player_fields = [
        "name",
        "second_name",
        "surname",
        "photo",
    ]

    # GOALS
    goals = (
        goal_events
        .filter(player__isnull=False)
        .values(
            "player",
            "player__name",
            "player__second_name",
            "player__surname",
            "player__photo",
            "team",
            "team__name",
            "team__age_group__name",
        )
        .annotate(goals=Count("id"))
    )

    # ASSISTS
    assists = (
        goal_events
        .filter(assist_by__isnull=False)
        .values(
            "assist_by",
            "assist_by__name",
            "assist_by__second_name",
            "assist_by__surname",
            "assist_by__photo",
            "team",
            "team__name",
            "team__age_group__name",
        )
        .annotate(assists=Count("id"))
    )

    # PRE-ASSISTS
    pre_assists = (
        goal_events
        .filter(pre_assist_by__isnull=False)
        .values(
            "pre_assist_by",
            "pre_assist_by__name",
            "pre_assist_by__second_name",
            "pre_assist_by__surname",
            "pre_assist_by__photo",
            "team",
            "team__name",
            "team__age_group__name",
        )
        .annotate(pre_assists=Count("id"))
    )

    players = {}

    # Helper function to create player statistics
    def get_player_entry(player_id, team_id, item, prefix):
        key = (player_id, team_id)

        if key not in players:
            players[key] = {
                "player": player_id,
                "first_name": item[f"{prefix}name"],
                "second_name": item[f"{prefix}second_name"],
                "surname": item[f"{prefix}surname"],

                "photo": (
                    default_storage.url(item[f"{prefix}photo"])
                    if item[f"{prefix}photo"]
                    else ""
                ),

                "team": team_id,
                "team_name": item["team__name"],
                "age_group": item["team__age_group__name"],
                "goals": 0,
                "assists": 0,
                "pre_assists": 0,
            }

        return players[key]

    # Add goals
    for item in goals:
        entry = get_player_entry(
            item["player"],
            item["team"],
            item,
            "player__",
        )
        entry["goals"] = item["goals"]

    # Add assists
    for item in assists:
        entry = get_player_entry(
            item["assist_by"],
            item["team"],
            item,
            "assist_by__",
        )
        entry["assists"] = item["assists"]

    # Add pre-assists
    for item in pre_assists:
        entry = get_player_entry(
            item["pre_assist_by"],
            item["team"],
            item,
            "pre_assist_by__",
        )
        entry["pre_assists"] = item["pre_assists"]

    # Final player list
    player_statistics = list(players.values())

    player_statistics.sort(
        key=lambda x: (
            -x["goals"],
            -x["assists"],
            -x["pre_assists"],
            x["first_name"] or "",
        )
    )

    context = {
        "competition_season": competition_season,
        "player_statistics": player_statistics,
        "start_date": start_date or "",
        "end_date": end_date or "",
    }

    return render(
        request,
        "matches_app/competition_season/competition_season_goal_scorers.html",
        context,
    )
