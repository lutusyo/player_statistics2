from django.shortcuts import render, get_object_or_404
from lineup_app.models import MatchLineup
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

def match_lineup_view(request, match_id):
    match = get_object_or_404(Match, id=match_id)

    # Get starting XI for the home team (you can do the same for away)
    home_lineup_qs = (
        MatchLineup.objects
        .filter(match=match, is_starting=True, team=match.home_team)
        .select_related("player")
        .order_by("order")
    )

    home_lineup = []
    for lineup in home_lineup_qs:
        pos = POSITION_COORDS.get(lineup.position, {"top": 0, "left": 0})
        home_lineup.append({
            "name": lineup.player.name,
            "number": lineup.player.shirt_number,  # Assuming Player model has this
            "top": pos["top"],
            "left": pos["left"],
        })

    return render(request, "lineup_app/match_lineup.html", {
        "match": match,
        "home_lineup": home_lineup,
        "active_tab": "lineup",
    })
