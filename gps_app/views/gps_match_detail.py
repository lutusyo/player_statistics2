import json
from django.shortcuts import render, get_object_or_404
from gps_app.models import GPSRecord
from matches_app.models import Match
from gps_app.utils.gps_match_detail import get_gps_context  # ✅ Import the utility

def gps_match_detail(request, match_id):
    match = get_object_or_404(Match, id=match_id)

    # ✅ Use the utility to get the GPS context
    gps_context = get_gps_context(match)

    # ✅ Add match into context if not already present
    gps_context['match'] = match

    return render(request, 'gps_app/gps_match_detail.html', gps_context)
