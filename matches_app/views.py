from django.shortcuts import render, get_object_or_404
from .models import Match, PlayerMatchStats
from players_app.models import PlayerCareerStage, Player
from django.db.models import Sum, Count
from django.contrib.auth.decorators import login_required
from datetime import date



@login_required
def team_dashboard(request, team):
    players = Player.objects.filter(age_group=team)

    position_order = ['Goalkeeper', 'Defender', 'Midfielder', 'Forward']
    selected_age_group = request.GET.get('age_group')


    #group players by position

    grouped_players = {}
    for position in position_order:
        grouped_players[position] = players.filter(position=position)



    context = {
        'team_selected': team,
        'selected_age_group': selected_age_group,
        'players': players,
        'position_order': position_order,
        'grouped_players': grouped_players,
        'active_tab': 'fixtures'
    }
    return render(request, 'matches_app/fixtures.html', context)


@login_required
def player_statistics_view(request, team):
    selected_season = request.GET.get('season')
    selected_age_group = request.GET.get('age_group')
    selected_competition = request.GET.get('competition')

    matches = Match.objects.all()
    seasons = dict(Match._meta.get_field('season').choices)
    competitions = dict(Match._meta.get_field('competition_type').choices)
    age_groups = dict(Player._meta.get_field('age_group').choices)

    stats = PlayerMatchStats.objects.select_related('player', 'match')
    players = Player.objects.filter(age_group=team)

    if selected_season:
        stats = stats.filter(match__season=selected_season)

    if selected_age_group:
        stats = stats.filter(player__age_group=selected_age_group)
        players = players.filter(age_group=selected_age_group)

    if selected_competition:
        stats = stats.filter(match__competition_type=selected_competition)

    player_data = []
    for player in players:
        player_stats = stats.filter(player=player)
        appearances = player_stats.count()
        goals = player_stats.aggregate(Sum('goals'))['goals__sum'] or 0
        assists = player_stats.aggregate(Sum('assists'))['assists__sum'] or 0
        minutes = player_stats.aggregate(Sum('minutes_played'))['minutes_played__sum'] or 0

        

        player_info = {
            'player': player,
            'appearances': appearances,
            'goals': goals,
            'assists': assists,
            'minutes': minutes,
        }

        # Only include goalkeeper stats if the player is a goalkeeper
        if player.position == 'Goalkeeper':
            player_info.update({
                'saves_success_rate': round(player_stats.aggregate(Sum('saves_success_rate'))['saves_success_rate__sum'] or 0, 2),
                'clean_sheets': player_stats.aggregate(Sum('clean_sheets'))['clean_sheets__sum'] or 0,
                'catches': player_stats.aggregate(Sum('catches'))['catches__sum'] or 0,
                'punches': player_stats.aggregate(Sum('punches'))['punches__sum'] or 0,
                'drops': player_stats.aggregate(Sum('drops'))['drops__sum'] or 0,
                'penalties_saved': player_stats.aggregate(Sum('penalties_saved'))['penalties_saved__sum'] or 0,
                'clearances': player_stats.aggregate(Sum('clearances'))['clearances__sum'] or 0,

                #distribution
                'total_passes': player_stats.aggregate(Sum('total_passes'))['total_passes__sum'] or 0,
                'pass_success_rate': round(player_stats.aggregate(Sum('pass_success_rate'))['pass_success_rate__sum'] or 0, 2),
                'long_pass_success': round(player_stats.aggregate(Sum('long_pass_success'))['long_pass_success__sum'] or 0, 2),

                # discpline
                'fouls_won': player_stats.aggregate(Sum('fouls_won'))['fouls_won__sum'] or 0,
                'fouls_conceded': player_stats.aggregate(Sum('fouls_conceded'))['fouls_conceded__sum'] or 0,
                'yellow_cards': player_stats.aggregate(Sum('yellow_cards'))['yellow_cards__sum'] or 0,
                'red_cards': player_stats.aggregate(Sum('red_cards'))['red_cards__sum'] or 0,
            })

        player_data.append(player_info)

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
    upcoming_matches = Match.objects.filter(team=team, date__gte=date.today()).order_by('date')
    past_matches = Match.objects.filter(team=team, date__lt=date.today()).order_by('-date')

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

    context = {
        'team': team,
        'team_selected': team,
        'active_tab': 'table',
        }
    return render(request, 'teams_app/table.html', context)



