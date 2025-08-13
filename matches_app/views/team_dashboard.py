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
def team_dashboard_view(request, team_id):

    team = Team.objects.get(id=team_id)

    # Just redirect to the fixtures view
    return redirect('matches_app:team_fixtures', team=team.age_group.code)