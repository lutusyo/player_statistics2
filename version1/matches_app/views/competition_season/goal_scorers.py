from version1.tagging_app.models import AttemptToGoal
from django.shortcuts import get_object_or_404, render
from version1.matches_app.models import CompetitionSeason
from datetime import date

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from version1.matches_app.forms import MatchResultForm
from version1.matches_app.models import Match

from django.db.models import Count

def competition_season_goal_scorers(request, competition_season_id):

    competition_season = get_object_or_404(CompetitionSeason, id=competition_season_id, is_active=True,)

    # Get all finished matches in this competition season
    finished_matches = competition_season.matches.filter(result_status="FINISHED")

    # Get goal attempts that are recorded as goals
    goal_events = (AttemptToGoal.objects.filter(
            match__in=finished_matches,
            outcome="On Target Goal",
            player__isnull=False,
            is_own_goal=False,
        )
        .select_related("player","team",)
    )

    # Count goals by player and team
    goal_scorers = (
        goal_events
        .values(
            "player",
            "player__name",
            "team",
            "team__name",
        )
        .annotate(goals=Count("id"))
        .order_by(
            "-goals",
            "player__name",
        )
    )

    context = {
        "competition_season": competition_season,
        "goal_scorers": goal_scorers,
    }

    return render(request,"matches_app/competition_season/competition_season_goal_scorers.html", context,)