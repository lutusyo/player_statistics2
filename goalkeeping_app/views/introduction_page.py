from django.shortcuts import render, get_object_or_404
from tagging_app.models import Match


def goalkeeping_intro(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    context = {
        'match': match,
        'home_team': match.home_team,
        'away_team': match.away_team,
        'title': 'GOALKEPING',
        'company': 'Azam Fc Analyst',
    }
    return render(request, 'goalkeeping_app/intro_page.html', context)
