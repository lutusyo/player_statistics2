# reports_app/views/match_summary_stats.py
from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Sum, F
from matches_app.models import Match
from tagging_app.models import AttemptToGoal, PassEvent
from lineup_app.models import MatchLineup, Substitution
from defensive_app.models import PlayerDefensiveStats  # optional
from teams_app.models import Team
from gps_app.models import GPSRecord  # added for distance data
from reports_app.utils.stats import get_match_stats
from matches_app.models import Match
from django.shortcuts import render, get_object_or_404

def match_summary_stats_view(request, match_id):
    match = get_object_or_404(Match, id=match_id)  
    context = get_match_stats(match)              

    return render(request, 'reports_app/match_summary_stats.html', context)