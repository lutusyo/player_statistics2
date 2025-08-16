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


def get_match_goals(match):
    goals_qs = AttemptToGoal.objects.filter(match=match, outcome='On Target Goal')
    home_ids = MatchLineup.objects.filter(match=match, team=match.home_team).values_list('player_id', flat=True)
    away_ids = MatchLineup.objects.filter(match=match, team=match.away_team).values_list('player_id', flat=True)

    home_goals = 0
    away_goals = 0

    for goal in goals_qs:
        if goal.player_id in home_ids or goal.team_id == match.home_team_id:
            home_goals += 1
        elif goal.player_id in away_ids or goal.team_id == match.away_team_id:
            away_goals += 1

    return home_goals, away_goals