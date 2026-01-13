from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET
from lineup_app.models import MatchLineup
from matches_app.models import Match

@require_GET
def api_current_on_field_players(request, match_id):
    """
    Returns only players currently on the pitch for a match.
    Shared by Attempt-to-Goal and Pass Network panels.
    """
    match = get_object_or_404(Match, id=match_id)

    lineups = (
        MatchLineup.objects
        .filter(match=match, time_in__isnull=False, time_out__isnull=True)
        .select_related("player", "team")
        .order_by("order", "player__name")
    )


    players = [
        {
            "id": l.player.id,
            "name": l.player.full_name,   # ✅ FULL NAME
            "jersey_number": l.player.jersey_number,
            "photo_url": l.player.photo.url if l.player.photo else "",
            "team_name": l.team.name if l.team else "",
            "team_id": l.team.id if l.team else None,
        }
        for l in lineups
    ]

    return JsonResponse({"players": players})
