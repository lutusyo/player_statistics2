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



@login_required
def player_statistics_view(request, team):
    selected_season = request.GET.get('season')
    selected_age_group = request.GET.get('age_group')
    selected_competition = request.GET.get('competition')

    seasons = dict(Match._meta.get_field('season').choices)
    competitions = dict(Match._meta.get_field('competition_type').choices)
    age_groups = AgeGroup.objects.all()

    players = Player.objects.filter(age_group__code=team)

    if selected_age_group:
        players = players.filter(age_group__code=selected_age_group)

    def get_stats(player, comp_type):
        matches = Match.objects.filter(
            competition_type=comp_type,
        )

        if selected_season:
            matches = matches.filter(season=selected_season)
        if selected_age_group:
            matches = matches.filter(age_group__code=selected_age_group)

        appearances = MatchLineup.objects.filter(player=player, match__in=matches).count()
        goals = AttemptToGoal.objects.filter(player=player, match__in=matches, outcome='On Target Goal').count()

        return {'appearances': appearances, 'goals': goals}

    player_data = []

    for player in players:
        local = get_stats(player, 'Local Friendly')
        international = get_stats(player, 'International Friendly')
        nbc = get_stats(player, 'NBC Youth League')

        player_data.append({
            'player': player,
            'local_ap': local['appearances'],
            'local_gl': local['goals'],
            'int_ap': international['appearances'],
            'int_gl': international['goals'],
            'nbc_ap': nbc['appearances'],
            'nbc_gl': nbc['goals'],
            'total_ap': local['appearances'] + international['appearances'] + nbc['appearances'],
            'total_gl': local['goals'] + international['goals'] + nbc['goals'],
        })

    context = {
        'seasons': seasons,
        'competitions': competitions,
        'age_groups': age_groups,
        'selected_season': selected_season,
        'selected_age_group': selected_age_group,
        'selected_competition': selected_competition,
        'player_data': player_data,
        'team_selected': team,
    }

    return render(request, 'matches_app/players_statistics.html', context)


