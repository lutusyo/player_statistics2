from django.shortcuts import get_object_or_404, render
from version1.matches_app.models import CompetitionSeason
from datetime import date

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from version1.matches_app.forms import MatchResultForm
from version1.matches_app.models import Match

def competition_season_dashboard(request, competition_season_id):
    competition_season = get_object_or_404(CompetitionSeason, id=competition_season_id, is_active=True,)
    participating_teams = (competition_season.participating_teams.filter(is_active=True).select_related("team", "team__age_group"))

    upcoming_matches = (competition_season.matches
        .filter(date__gte=date.today())
        .select_related("home_team","away_team","venue",)
        .order_by("date", "time")[:5]
    )

    recent_matches = (competition_season.matches
        .filter(date__lt=date.today())
        .select_related("home_team","away_team","venue",)
        .order_by("-date", "-time")[:5]
    )

    context = {
        "competition_season": competition_season,
        "participating_teams": participating_teams,
        "upcoming_matches": upcoming_matches,
        "recent_matches": recent_matches,
    }

    return render(request, "matches_app/competition_season/competition_season_dashboard.html", context,)