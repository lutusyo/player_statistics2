from django.shortcuts import get_object_or_404, render
from version1.matches_app.models import CompetitionSeason
from datetime import date

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from version1.matches_app.forms import MatchResultForm
from version1.matches_app.models import Match



def competition_season_fixtures(request, competition_season_id):
    competition_season = get_object_or_404(
        CompetitionSeason,
        id=competition_season_id,
        is_active=True,
    )

    fixtures = (competition_season.matches
        .filter(result_status__in=["SCHEDULED", "LIVE"],
        )
        .select_related(
            "home_team",
            "away_team",
            "venue",
        )
        .order_by("date", "time")
    )

    context = {
        "competition_season": competition_season,
        "fixtures": fixtures,
    }

    return render(request, "matches_app/competition_season/competition_season_fixtures.html", context,)
