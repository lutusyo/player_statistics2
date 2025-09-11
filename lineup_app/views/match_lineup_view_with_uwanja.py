from django.shortcuts import render, get_object_or_404
from lineup_app.models import MatchLineup, PositionChoices
from matches_app.models import Match
from django.http import JsonResponse
from django.db import transaction
from players_app.models import Player

from django.shortcuts import render, get_object_or_404
from lineup_app.models import MatchLineup, PositionChoices
from matches_app.models import Match

# Map position codes to pitch coordinates (% from top, % from left)
POSITION_COORDS = {
    "GK":  {"top": 5,  "left": 45},
    "RB":  {"top": 25, "left": 80},
    "RCB": {"top": 25, "left": 60},
    "LCB": {"top": 25, "left": 40},
    "LB":  {"top": 25, "left": 20},
    "RM":  {"top": 50, "left": 75},
    "CM":  {"top": 50, "left": 55},
    "LM":  {"top": 50, "left": 35},
    "RW":  {"top": 75, "left": 70},
    "LW":  {"top": 75, "left": 30},
    "ST":  {"top": 75, "left": 50},
}

def pitch_lineup_view(request, match_id):
    match = get_object_or_404(Match, id=match_id)

    # Get starters
    home_starters = MatchLineup.objects.filter(match=match, team=match.home_team, is_starting=True).select_related('player')
    away_starters = MatchLineup.objects.filter(match=match, team=match.away_team, is_starting=True).select_related('player')

    def lineup_with_coords(qs, mirror=False):
        players = []
        for ml in qs:
            coords = POSITION_COORDS.get(ml.position, {"top": 50, "left": 50})
            top = coords["top"]
            if mirror:
                top = 100 - top
            players.append({
                "id": ml.player.id,
                "name": ml.player.name,
                "number": getattr(ml.player, "jersey_number", ""),
                "position_x": coords["left"],
                "position_y": top,
            })
        return players

    home_lineup = lineup_with_coords(home_starters)
    away_lineup = lineup_with_coords(away_starters, mirror=True)

    lineup = home_lineup + away_lineup

    return render(request, "lineup_app/pitch_lineup.html", {
        "match": match,
        "lineup": lineup,
        "home_lineup": home_lineup,
        "away_lineup": away_lineup,
    })

