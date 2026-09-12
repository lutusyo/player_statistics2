from django.shortcuts import get_object_or_404, render
from version1.matches_app.models import CompetitionSeason
from datetime import date

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from version1.matches_app.forms import MatchResultForm
from version1.matches_app.models import Match




def competition_season_results(request, competition_season_id):
    competition_season = get_object_or_404(CompetitionSeason,
        id=competition_season_id,
        is_active=True,
    )

    results = (competition_season.matches.filter(result_status="FINISHED")
        .select_related("home_team", "away_team", "venue",)
        .order_by("-date", "-time")
    )

    context = {
        "competition_season": competition_season,
        "results": results,
    }

    return render(request, "matches_app/competition_season/competition_season_results.html", context,)