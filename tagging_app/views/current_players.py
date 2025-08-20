from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from lineup_app.models import MatchLineup
from matches_app.models import Match

def api_current_players(request, match_id):
    """
    Return only players currently on the pitch for a match.
    Shared by Attempt-to-Goal and Pass Network panels.
    """
    match = get_object_or_404(Match, id=match_id)

    lineups = (
        MatchLineup.objects
        .filter(match=match, time_out__isnull=True)
        .select_related("player", "team")
    )

    players = [
        {
            "id": l.player.id,
            "name": l.player.name,
            "photo_url": l.player.photo.url if l.player.photo else "",
            "team_name": l.team.name if l.team else "",
            "team_id": l.team.id if l.team else None,  # <-- add this
        }
        for l in lineups
    ]

    return JsonResponse({"players": players})
