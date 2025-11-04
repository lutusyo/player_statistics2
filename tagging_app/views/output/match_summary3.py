from django.shortcuts import render, get_object_or_404
from matches_app.models import Match
from lineup_app.models import MatchLineup, POSITION_COORDS

def match_summary_view(request, match_id, team_id):
    match = get_object_or_404(Match, id=match_id)

    # Fetch lineup for the team
    lineup_qs = MatchLineup.objects.filter(match=match, team_id=team_id).select_related("player")

    lineup = []
    substitutes = []

    for l in lineup_qs:
        # Ensure minutes_played is calculated
        player_data = {
            "id": l.id,
            "name": l.player.name,
            "number": l.player.jersey_number,
            "position": l.position,
            "minutes_played": l.minutes_played,
            "photo": l.player.photo.url if l.player.photo else None,
            # Use formation-specific coordinates if available
            **POSITION_COORDS.get(l.formation, {}).get(l.position, {"top": 50, "left": 50})
        }

        if l.is_starting:
            lineup.append(player_data)
        else:
            if l.minutes_played > 0:
                substitutes.append(player_data)

    context = {
        "match": match,
        "lineup": lineup,        # Starting XI
        "substitutes": substitutes,  # Bench players who played
    }

    return render(request, "tagging_app/output/match_summary3.html", context)
