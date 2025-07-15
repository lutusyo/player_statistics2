# actions_app/views.py

from django.shortcuts import render, get_object_or_404
from .models import TeamActionStats
from matches_app.models import Match

def match_action_stats(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    team_stats = TeamActionStats.objects.filter(match=match)
    return render(request, 'actions_app/match_action_stats.html', {
        'match': match,
        'team_stats': team_stats,  # renamed from team_action_stats
    })
