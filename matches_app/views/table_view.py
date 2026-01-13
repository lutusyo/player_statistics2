# matches_app/views.py
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from players_app.models import PlayerCareerStage, Player
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from reportlab.lib.pagesizes import A4
from datetime import date

from django.db.models import Q
from teams_app.models import Team, AgeGroup
from lineup_app.models import MatchLineup
from matches_app.models import Match
from tagging_app.models import AttemptToGoal, GoalkeeperDistributionEvent
from collections import Counter

from collections import defaultdict
from matches_app.views.get_match_goals import get_match_goals
from django.shortcuts import render, get_object_or_404
from matches_app.utils.league_table import build_league_table
from matches_app.models import CompetitionType, SeasonChoices
from django.contrib.auth.decorators import login_required




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
    'code' is the AgeGroup code of the team.
    """
    age_group = get_object_or_404(AgeGroup, code=code)

    # Filters (auto from GET params, with defaults)
    competition = request.GET.get("competition", CompetitionType.NBC_YOUTH_LEAGUE)
    season = request.GET.get("season", SeasonChoices.SEASON_2025_2026)

    # Build league table filtered by this age group
    table = build_league_table(
        competition_type=competition,
        season=season,
        age_group=age_group
    )

    context = {
        "active_tab": "table",
        "team_selected": age_group.code,  # ensures base template links work

        # table data
        "league_table": table,
        "competition": competition,
        "season": season,
        "age_group": age_group,

        # filter options
        "competitions": CompetitionType.choices,
        "seasons": SeasonChoices.choices,
        "age_groups": AgeGroup.objects.all(),
    }

    return render(request, "matches_app/league_table.html", context)


def league_table_view(request):
    """
    General league table view (not tied to a specific team)
    """
    # Filters (auto from GET params)
    competition = request.GET.get("competition", CompetitionType.NBC_YOUTH_LEAGUE)
    season = request.GET.get("season", SeasonChoices.SEASON_2025_2026)

    age_group_id = request.GET.get("age_group")
    age_group = None
    if age_group_id:
        age_group = AgeGroup.objects.filter(id=age_group_id).first()

    table = build_league_table(
        competition_type=competition,
        season=season,
        age_group=age_group
    )

    context = {
        "active_tab": "table",
        "team_selected": None,  # important: no team selected here

        # table data
        "league_table": table,
        "competition": competition,
        "season": season,
        "age_group": age_group,

        # filter options
        "competitions": CompetitionType.choices,
        "seasons": SeasonChoices.choices,
        "age_groups": AgeGroup.objects.all(),
    }

    return render(request, "matches_app/league_table.html", context)
