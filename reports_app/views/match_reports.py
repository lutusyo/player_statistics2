from django.shortcuts import render, get_object_or_404
from lineup_app.models import Match, MatchLineup, Substitution
from tagging_app.models import AttemptToGoal, PassEvent  # adjust to your app name
from reports_app.utils.stats import get_match_stats
from matches_app.models import Match
from django.shortcuts import render, get_object_or_404

def match_summary_view(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    context = get_match_stats(match)               

    return render(request, 'reports_app/match_summary.html', context)
