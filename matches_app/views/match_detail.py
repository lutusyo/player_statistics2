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
def match_detail(request, match_id):
    match = get_object_or_404(Match, pk=match_id)

    # Get all attempts with outcome 'On Target Goal' for this match
    goals_qs = AttemptToGoal.objects.filter(match=match, outcome='On Target Goal').select_related('player', 'team', 'assist_by')

    # Get home and away players IDs for this match
    home_player_ids = MatchLineup.objects.filter(match=match, team=match.home_team).values_list('player_id', flat=True)
    away_player_ids = MatchLineup.objects.filter(match=match, team=match.away_team).values_list('player_id', flat=True)

    home_goals = 0
    away_goals = 0
    goals = []

    for goal in goals_qs:
        # Determine if goal belongs to home or away by player team or by lineup player ID
        if goal.player_id in home_player_ids:
            home_goals += 1
            team_name = match.home_team.name
        elif goal.player_id in away_player_ids:
            away_goals += 1
            team_name = match.away_team.name
        else:
            # fallback if player not in lineup, fallback to AttemptToGoal team FK
            if goal.team_id == match.home_team_id:
                home_goals += 1
                team_name = match.home_team.name
            elif goal.team_id == match.away_team_id:
                away_goals += 1
                team_name = match.away_team.name
            else:
                team_name = "Unknown"

        goals.append({
            'minute': goal.minute,
            'second': goal.second,
            'scorer': goal.player.name if goal.player else "Unknown",
            'assist_by': goal.assist_by.name if goal.assist_by else None,
            'is_own_goal': False,  # Adjust here if you have own goal info
            'team_name': team_name,
        })

    return render(request, 'matches_app/match_details.html', {
        'match': match,
        'home_team_name': match.home_team.name,
        'away_team_name': match.away_team.name,
        'home_team_goals': home_goals,
        'away_team_goals': away_goals,
        'goals': goals,
    })