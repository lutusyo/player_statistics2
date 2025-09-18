# perfomance_rating_app/views.py
from django.shortcuts import render, get_object_or_404
from perfomance_rating_app.models import PerformanceRating
from perfomance_rating_app.services import compute_player_rating
from matches_app.models import Match
from players_app.models import Player

def _star_color_for_score(score):
    """
    Map numeric score (1-5) -> color class name.
    Adjust these mappings as you prefer.
    """
    try:
        s = int(score)
    except Exception:
        s = 0
    if s >= 5:
        return 'green'
    if s == 4:
        return 'teal'
    if s == 3:
        return 'yellow'
    if s == 2:
        return 'orange'
    return 'red'

def _make_star_list(score):
    """Return list of 5 dicts: {filled: bool, color: 'green'|'orange'...}"""
    color = _star_color_for_score(score)
    stars = []
    for i in range(1, 6):
        stars.append({'filled': i <= score, 'color': color})
    return stars

def match_performance(request, match_id):
    match = get_object_or_404(Match, id=match_id)

    # Combine home + away players and remove duplicates
    players_qs = match.home_team.players.all() | match.away_team.players.all()
    players = players_qs.distinct()

    ratings_for_template = []
    for player in players:
        rating = PerformanceRating.objects.filter(player=player, match=match).first()
        if not rating or not rating.is_computed:
            rating = compute_player_rating(player, match)

        # build star lists for each metric
        attacking_stars = _make_star_list(getattr(rating, 'attacking', 0))
        creativity_stars = _make_star_list(getattr(rating, 'creativity', 0))
        defending_stars = _make_star_list(getattr(rating, 'defending', 0))
        tactical_stars = _make_star_list(getattr(rating, 'tactical', 0))
        technical_stars = _make_star_list(getattr(rating, 'technical', 0))
        discipline_stars = _make_star_list(getattr(rating, 'discipline', 5))

        # average
        avg = round((
            (getattr(rating, 'attacking',0) +
             getattr(rating, 'creativity',0) +
             getattr(rating, 'defending',0) +
             getattr(rating, 'tactical',0) +
             getattr(rating, 'technical',0) +
             getattr(rating, 'discipline',5))
            / 6
        ), 1)

        # payload for template
        ratings_for_template.append({
            'player': player,
            'rating': rating,
            'attacking_stars': attacking_stars,
            'creativity_stars': creativity_stars,
            'defending_stars': defending_stars,
            'tactical_stars': tactical_stars,
            'technical_stars': technical_stars,
            'discipline_stars': discipline_stars,
            'average': avg,
            'radar_dataset': [
                getattr(rating, 'attacking', 0),
                getattr(rating, 'creativity', 0),
                getattr(rating, 'defending', 0),
                getattr(rating, 'tactical', 0),
                getattr(rating, 'technical', 0),
                getattr(rating, 'discipline', 5),
            ]
        })

    # Sort players by average descending
    ratings_for_template.sort(key=lambda x: x['average'], reverse=True)

    return render(request, 'performance_rating_app/match_performance.html', {
        'match': match,
        'ratings': ratings_for_template,
    })

