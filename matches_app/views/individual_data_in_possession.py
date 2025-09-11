from django.shortcuts import render, get_object_or_404
from matches_app.models import Match
from tagging_app.utils.individual_data_in_possession_util import get_match_in_possession_data

def individual_data_in_possession_view(request, match_id):
    match = get_object_or_404(Match, id=match_id)

    # all players for both teams
    stats = get_match_in_possession_data(match)

    context = {
        "match": match,
        "stats": stats,
    }
    return render(request, "matches_app/partials/individual_data_in_possession.html", context)
