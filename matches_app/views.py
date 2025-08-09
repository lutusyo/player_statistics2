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
from .models import MatchLineup, Match
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



def match_lineup_view(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    starting_players = MatchLineup.objects.filter(match=match, is_starting=True)
    substitutes = MatchLineup.objects.filter(match=match, is_starting=False)

    # Assign coordinates based on position
    for p in starting_players:
        pos = p.position
        coords = POSITION_COORDINATES.get(pos, {'x': 0, 'y': 0})
        p.position_x = coords['x']
        p.position_y = coords['y']

    context = {
        'match': match,
        'starting_players': starting_players,
        'substitutes': substitutes,
    }
    return render(request, 'matches_app/match_lineup.html', context)

@login_required
def team_dashboard_view(request, team_id):

    team = Team.objects.get(id=team_id)

    # Just redirect to the fixtures view
    return redirect('matches_app:team_fixtures', team=team.age_group.code)

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





@login_required
def career_stage_detail(request, stage_id):
    stage = get_object_or_404(PlayerCareerStage, id=stage_id)
    selected_age_group = request.GET.get('age_group')

    context = {
        'stage': stage,
        'selected_age_group': selected_age_group,

    }

    return render(request, 'matches_app/career_stage_detail.html', context)




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


@login_required
def fixtures_view(request, team):
    age_group = AgeGroup.objects.get(code=team)
    our_teams = Team.objects.filter(age_group=age_group, team_type='OUR_TEAM')

    upcoming_matches = Match.objects.filter(
        Q(home_team__in=our_teams) | Q(away_team__in=our_teams),
        date__gte=date.today()
    ).order_by('date')

    for match in upcoming_matches:
        match.home_goals, match.away_goals = get_match_goals(match)

    context = {
        'team': team,
        'upcoming_matches': upcoming_matches,
        'team_selected': team,
        'active_tab': 'fixtures',
    }
    return render(request, 'matches_app/fixtures.html', context)


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


@login_required
def table_view(request, code):
    age_group = get_object_or_404(AgeGroup, code=code)

    context = {
        'age_group_selected': age_group,
        'active_tab': 'table',
        'team_selected': age_group.code, 
    }
    return render(request, 'matches_app/matches_table.html', context)



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








