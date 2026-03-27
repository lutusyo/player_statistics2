# matches_app/views.py
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from version1.players_app.models import PlayerCareerStage, Player
from django.db.models import Sum, Q
from django.contrib.auth.decorators import login_required
from reportlab.lib.pagesizes import A4
from datetime import date

from version1.teams_app.models import Team, AgeGroup
from version1.lineup_app.models import MatchLineup
from version1.matches_app.models import Match, Competition
from version1.tagging_app.models import AttemptToGoal, GoalkeeperDistributionEvent
from collections import Counter, defaultdict

from version1.matches_app.views.get_match_goals import get_match_goals
from version1.matches_app.utils.league_table import build_league_table
from version1.matches_app.models import CompetitionType, SeasonChoices


# position coordinates (x: left-right %, y: top-bottom %)
POSITION_COORDINATES = {
    'GK': {'x': 50, 'y': 95},

    'LB': {'x': 15, 'y': 80},
    'CB': {'x': 40, 'y': 80},
    'RB': {'x': 65, 'y': 80},

    'DM': {'x': 50, 'y': 65},

    'CM': {'x': 50, 'y': 50},
    'AM': {'x': 50, 'y': 35},

    'LW': {'x': 20, 'y': 30},
    'RW': {'x': 80, 'y': 30},
    'ST': {'x': 50, 'y': 20},
}



@login_required
def table_view(request, code):
    """
    Team-specific league table view.
    """
    age_group = get_object_or_404(AgeGroup, code=code)

    # ✅ Competition MUST be ID
    competition_id = request.GET.get("competition")
    season = request.GET.get("season", SeasonChoices.SEASON_2025_2026)

    competition = None
    if competition_id:
        competition = get_object_or_404(Competition, id=competition_id)

    table = build_league_table(
        competition=competition,
        season=season,
        age_group=age_group
    )

    context = {
        "active_tab": "table",
        "team_selected": age_group.code,

        "league_table": table,
        "competition_selected": competition_id,
        "season_selected": season,
        "age_group": age_group,

        # dropdowns
        "competitions": Competition.objects.all(),
        "seasons": SeasonChoices.choices,
    }

    return render(request, "matches_app/league_table.html", context)



def league_table_view(request):
    """
    General league table view (not tied to a specific team)
    """
    # Filters (auto from GET params)
    competition_id = request.GET.get("competition")  # get numeric ID
    season = request.GET.get("season", SeasonChoices.SEASON_2025_2026)

    competition = None
    if competition_id:
        try:
            competition = Competition.objects.get(id=int(competition_id))
        except (ValueError, Competition.DoesNotExist):
            competition = None

    age_group_id = request.GET.get("age_group")
    age_group = None
    if age_group_id:
        age_group = AgeGroup.objects.filter(id=age_group_id).first()

    # Pass `competition` object, not competition_type
    table = build_league_table(
        competition=competition,
        season=season,
        age_group=age_group
    )

    context = {
        "active_tab": "table",
        "team_selected": None,  # important: no team selected here

        # table data
        "league_table": table,
        "competition_selected": competition_id,
        "season_selected": season,
        "age_group": age_group,

        # filter options
        "competitions": Competition.objects.all(),
        "seasons": SeasonChoices.choices,
        "age_groups": AgeGroup.objects.all(),
    }

    return render(request, "matches_app/league_table.html", context)
