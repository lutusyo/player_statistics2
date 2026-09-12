from django.shortcuts import get_object_or_404, render
from version1.matches_app.models import CompetitionSeason
from datetime import date

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from version1.matches_app.forms import MatchResultForm
from version1.matches_app.models import Match




def competition_season_teams(request, competition_season_id):
    competition_season = get_object_or_404(CompetitionSeason, id=competition_season_id, is_active=True,)

    teams = (
        competition_season.participating_teams
        .filter(is_active=True)
        .select_related(
            "team",
            "team__age_group",
            "team__country",
            "team__region",
        )
        .order_by("team__name")
    )

    context = {
        "competition_season": competition_season,
        "teams": teams,
    }

    return render(request, "matches_app/competition_season/competition_season_teams.html", context,)