from django.shortcuts import render, get_object_or_404
from .models import Match, PlayerMatchStats
from players_app.models import PlayerCareerStage
from django.db.models import Sum, Count
from players_app.models import Player
from django.contrib.auth.decorators import login_required



@login_required
def player_statistics_view(request):
    selected_season = request.GET.get('season')
    selected_age_group = request.GET.get('age_group')
    selected_competition = request.GET.get('competition')

    matches = Match.objects.all()
    seasons = dict(Match._meta.get_field('season').choices)
    competitions = dict(Match._meta.get_field('competition_type').choices)
    age_groups = dict(Player._meta.get_field('age_group').choices)

    stats = PlayerMatchStats.objects.select_related('player', 'match')

    if selected_season:
        stats = stats.filter(match__season=selected_season)

    if selected_age_group:
        stats = stats.filter(player__age_group=selected_age_group)

    if selected_competition:
        stats = stats.filter(match__competition_type=selected_competition)

    players = Player.objects.all()
    if selected_age_group:
        players = players.filter(age_group=selected_age_group)

    player_data = []
    for player in players:
        player_stats = stats.filter(player=player)
        appearances = player_stats.count()
        goals = player_stats.aggregate(Sum('goals'))['goals__sum'] or 0
        assists = player_stats.aggregate(Sum('assists'))['assists__sum'] or 0
        minutes = player_stats.aggregate(Sum('minutes_played'))['minutes_played__sum'] or 0
        player_data.append({
            'player': player,
            'appearances': appearances,
            'goals': goals,
            'assists': assists,
            'minutes': minutes,
        })

    context = {
        'seasons': seasons,
        'age_groups': age_groups,
        'competitions': competitions,
        'selected_season': selected_season,
        'selected_age_group': selected_age_group,
        'selected_competition': selected_competition,
        'player_data': player_data,
    }
    return render(request, 'matches_app/players_statistics.html', context)

@login_required
def career_stage_detail(request, stage_id):
    stage = get_object_or_404(PlayerCareerStage, id=stage_id)
    return render(request, 'matches_app/career_stage_detail.html', {'stage': stage})