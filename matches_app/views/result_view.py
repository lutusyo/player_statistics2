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
from matches_app.models import MatchLineup, Match
from tagging_app.models import AttemptToGoal, GoalkeeperDistributionEvent
from collections import Counter

from collections import defaultdict
from matches_app.views.get_match_goals import get_match_goals

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
def results_view(request, team):
    age_group = AgeGroup.objects.get(code=team)
    our_teams = Team.objects.filter(age_group=age_group, team_type='OUR_TEAM')

    past_matches = Match.objects.filter(
        Q(home_team__in=our_teams) | Q(away_team__in=our_teams),
        date__lt=date.today()
    ).order_by('-date')

    for match in past_matches:
        match.home_goals, match.away_goals = get_match_goals(match)

    context = {
        "team": team,
        'team_selected': team,
        'past_matches': past_matches,
        'active_tab': 'results',
    }
    return render(request, 'matches_app/match_results.html', context)