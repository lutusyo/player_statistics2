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

    matches = Match.objects.all()
    seasons = dict(Match._meta.get_field('season').choices)
    competitions = dict(Match._meta.get_field('competition_type').choices)
    age_groups = AgeGroup.objects.all()

    stats = PlayerMatchStats.objects.select_related('player', 'match')
    players = Player.objects.filter(age_group__code=team)

    if selected_season:
        stats = stats.filter(match__season=selected_season)

    if selected_age_group:
        stats = stats.filter(player__age_group__code=selected_age_group)
        players = players.filter(age_group__code=selected_age_group)

    if selected_competition:
        stats = stats.filter(match__competition_type=selected_competition)

    # rest of your logic...




    player_data = []
    for player in players:
        player_stats = stats.filter(player=player)

        def get_stats_by_competition(comp):
            comp_stats = player_stats.filter(match__competition_type=comp)
            return {
                'appearances': comp_stats.count(),
                'goals': Goal.objects.filter(
                    match__in=comp_stats.values('match'),
                    scorer=player,
                    is_own_goal=False
                ).count()
            }

        local = get_stats_by_competition('Local Friendly')
        international = get_stats_by_competition('International Friendly')
        nbc = get_stats_by_competition('NBC Youth League')

        player_info = {
            'player': player,
            'local_ap': local['appearances'],
            'local_gl': local['goals'],
            'int_ap': international['appearances'],
            'int_gl': international['goals'],
            'nbc_ap': nbc['appearances'],
            'nbc_gl': nbc['goals'],
            'total_ap': local['appearances'] + international['appearances'] + nbc['appearances'],
            'total_gl': local['goals'] + international['goals'] + nbc['goals'],
        }

    context = {
        'seasons': seasons,
        'age_groups': age_groups,
        'competitions': competitions,
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

@login_required
def fixtures_view(request, team):
    # 'team' here is the age_group code, e.g. 'U17'
    # get our team(s) with this age group code
    age_group = AgeGroup.objects.get(code=team)
    our_teams = Team.objects.filter(age_group=age_group, team_type='OUR_TEAM')

    # filter matches where home_team or away_team is in our_teams
    upcoming_matches = Match.objects.filter(
        Q(home_team__in=our_teams) | Q(away_team__in=our_teams),
        date__gte=date.today()
    ).order_by('date')

    past_matches = Match.objects.filter(
        Q(home_team__in=our_teams) | Q(away_team__in=our_teams),
        date__lt=date.today()
    ).order_by('-date')

    context = {
        'team': team,
        'upcoming_matches': upcoming_matches,
        'past_matches': past_matches,
        'team_selected': team,
        'active_tab': 'fixtures',
    }
    return render(request, 'matches_app/fixtures.html', context)


@login_required
def results_view(request, team):

    context = {
        "team": team,
        'team_selected': team,
        'active_tab': 'results',
    }
    return render(request, 'matches_app/match_results.html', context)

@login_required
def table_view(request, team):
    # team is age_group code like 'U17'
    age_group = AgeGroup.objects.get(code=team)
    our_team = Team.objects.filter(age_group=age_group, team_type='OUR_TEAM').first()

    context = {
        'team': team,
        'team_selected': our_team,  # <-- pass the Team instance here
        'active_tab': 'table',
    }
    return render(request, 'teams_app/table.html', context)

@login_required
def match_detail(request, match_id):
    match = get_object_or_404(Match, pk=match_id)
    player_stats = PlayerMatchStats.objects.filter(match=match).select_related('player')
    goals = Goal.objects.filter(match=match).select_related('scorer', 'assist_by')
    team_result = TeamMatchResult.objects.filter(match=match).first()

    # Option 3: Both teams as a string
    team_str = f"{match.home_team} vs {match.away_team}"

    return render(request, 'matches_app/match_details.html', {
        'match': match,
        'player_stats': player_stats,
        'goals': goals,
        'team_result': team_result,
        'team_selected': team_str,
    })




