from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from matches_app.models import Match
from teams_app.models import Team

def match_performance_list(request, team_id):
    # Get the team object or return 404
    team = get_object_or_404(Team, id=team_id)

    # Get all matches where the team played as home or away
    matches = Match.objects.filter(Q(home_team=team) | Q(away_team=team)).order_by('-date')

    context = {
        'matches': matches,
        'team': team,
    }

    return render(request, 'performance_rating_app/match_performance_list.html', context)
