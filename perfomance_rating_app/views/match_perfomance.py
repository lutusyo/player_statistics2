# perfomance_rating_app/views.py
from django.shortcuts import render, redirect
from django.http import JsonResponse
from perfomance_rating_app.models import PerformanceRating
from matches_app.models import Match
from players_app.models import Player
from perfomance_rating_app.services import compute_player_rating  # We'll create this service function

# View to display and calculate ratings for a match
def match_performance(request, match_id):
    match = Match.objects.get(id=match_id)
    players = match.home_team.players.all() | match.away_team.players.all()

    # Calculate ratings for players in this match
    ratings = []
    for player in players:
        rating = PerformanceRating.objects.filter(player=player, match=match).first()
        if not rating or not rating.is_computed:
            rating = compute_player_rating(player, match)  # Call our service function
        ratings.append(rating)

    return render(request, 'performance_rating_app/match_performance.html', {
        'match': match,
        'ratings': ratings,
    })
