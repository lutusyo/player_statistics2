from version1.tagging_app.models import AttemptToGoal
from version1.matches_app.models import CompetitionSeason
from datetime import date
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from version1.matches_app.forms import MatchResultForm
from version1.matches_app.models import Match
from django.db.models import Count, Q
from version1.teams_app.models import Team

from django.shortcuts import get_object_or_404, render
from django.db.models import Count

from version1.tagging_app.models import AttemptToGoal
from version1.matches_app.models import CompetitionSeason


def competition_season_goal_scorers(request, competition_season_id):
    competition_season = get_object_or_404(
        CompetitionSeason,
        id=competition_season_id,
        is_active=True,
    )

    # Finished matches
    finished_matches = competition_season.matches.filter(
        result_status="FINISHED"
    )

    # ---------------------------------------------------------
    # GOALS
    # ---------------------------------------------------------
    goal_events = (
        AttemptToGoal.objects.filter(
            match__in=finished_matches,
            outcome="On Target Goal",
            player__isnull=False,
            is_own_goal=False,
        )
        .select_related(
            "player",
            "team",
            "team__age_group",
        )
    )

    goal_scorers = list(
        goal_events
        .values(
            "player",
            "player__name",
            "team",
            "team__name",
            "team__age_group__name",
        )
        .annotate(
            goals=Count("id"),
        )
        .order_by("-goals", "player__name")
    )

    # ---------------------------------------------------------
    # ASSISTS
    # ---------------------------------------------------------
    assist_events = (
        AttemptToGoal.objects.filter(
            match__in=finished_matches,
            outcome="On Target Goal",
            assist_by__isnull=False,
            is_own_goal=False,
        )
    )

    assists = {
        item["assist_by"]: item["assists"]
        for item in assist_events
        .values("assist_by")
        .annotate(assists=Count("id"))
    }

    # Add assists to each goal scorer
    for scorer in goal_scorers:
        scorer["assists"] = assists.get(scorer["player"], 0)

    context = {
        "competition_season": competition_season,
        "goal_scorers": goal_scorers,
    }

    return render(
        request,
        "matches_app/competition_season/competition_season_goal_scorers.html",
        context,
    )