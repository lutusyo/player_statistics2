# perfomance_rating_app/views.py
from players_app.models import Player
from perfomance_rating_app.models import PerformanceRating
from django.shortcuts import render

def player_season_ratings(request, player_id, season):
    player = Player.objects.get(id=player_id)
    ratings = PerformanceRating.objects.filter(player=player, match__season=season, is_computed=True)

    total = {
        'attacking': 0,
        'creativity': 0,
        'defending': 0,
        'tactical': 0,
        'technical': 0,
    }

    count = ratings.count()
    if count == 0:
        average = None
    else:
        for r in ratings:
            total['attacking'] += r.attacking or 0
            total['creativity'] += r.creativity or 0
            total['defending'] += r.defending or 0
            total['tactical'] += r.tactical or 0
            total['technical'] += r.technical or 0

        average = {key: round(val / count, 2) for key, val in total.items()}

    return render(request, 'performance_rating_app/player_season_ratings.html', {
        'player': player,
        'season': season,
        'average': average,
        'count': count,
    })
