from django.shortcuts import render, get_object_or_404
from matches_app.models import Match
from lineup_app.models import MatchLineup, POSITION_COORDS


def match_summary_view(request, match_id, team_id):
    match = get_object_or_404(Match, id=match_id)

    # Fetch all lineup for the team
    lineup_qs = MatchLineup.objects.filter(match=match, team_id=team_id).select_related("player")

    lineup = []
    substitutes = []

    for l in lineup_qs:
        player_data = {
            "id": l.id,
            "name": l.player.name,
            "number": l.player.jersey_number,
            "position": l.position,
            "minutes_played": l.minutes_played,  # use pre-calculated field
            **POSITION_COORDS.get(l.position, {"top": 50, "left": 50})
        }

        if l.is_starting:
            lineup.append(player_data)
        else:
            # Only include substitutes who played more than 0 minutes
            if l.minutes_played > 0:
                substitutes.append(player_data)

    # Optional: other lists for JS/template
    currently_on_pitch = [p for p in lineup_qs if p.time_in is not None and p.time_out is None]
    already_played_out = [p for p in lineup_qs if p.time_out is not None]
    subs_this_match = [p for p in lineup_qs if not p.is_starting and p.time_in is not None]
    subs_not_played = [p for p in lineup_qs if not p.is_starting and p.time_in is None]

    context = {
        "match": match,
        "lineup": lineup,               # Starting XI
        "substitutes": substitutes,     # Bench/subs (played > 0 min)
        "currently_on_pitch": currently_on_pitch,
        "already_played_out": already_played_out,
        "subs_this_match": subs_this_match,
        "subs_not_played": subs_not_played,
    }

    return render(request, "tagging_app/reports/match_summary3.html", context)
