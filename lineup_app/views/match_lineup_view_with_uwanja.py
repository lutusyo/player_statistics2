from django.shortcuts import render, get_object_or_404
from lineup_app.models import MatchLineup, POSITION_COORDS
from matches_app.models import Match


def pitch_lineup_view(request, match_id):
    match = get_object_or_404(Match, id=match_id)

    # --- Get home and away lineups ---
    home_qs = MatchLineup.objects.filter(match=match, team=match.home_team, is_starting=True).select_related('player')
    away_qs = MatchLineup.objects.filter(match=match, team=match.away_team, is_starting=True).select_related('player')

    # --- Determine formation for each team ---
    home_formation = home_qs.first().formation if home_qs.exists() else None
    away_formation = away_qs.first().formation if away_qs.exists() else None

    home_coords = POSITION_COORDS.get(home_formation, {})
    away_coords = POSITION_COORDS.get(away_formation, {})

    def lineup_with_coords(qs, coords_dict, mirror=False):
        """Attach pitch coordinates based on formation & mirror if away."""
        players = []
        for ml in qs:
            coords = coords_dict.get(ml.position, {"top": 50, "left": 50})
            top = coords["top"]
            left = coords["left"]

            # Mirror vertically for away team
            if mirror:
                top = 100 - top

            players.append({
                "id": ml.player.id,
                "name": ml.player.name,
                "number": getattr(ml.player, "jersey_number", ""),
                "position_x": left,
                "position_y": top,
                "photo": ml.player.photo.url if ml.player.photo else None,
                "position": ml.position,
            })
        return players

    home_lineup = lineup_with_coords(home_qs, home_coords)
    away_lineup = lineup_with_coords(away_qs, away_coords, mirror=True)

    context = {
        "match": match,
        "home_team": match.home_team,
        "away_team": match.away_team,
        "home_formation": home_formation,
        "away_formation": away_formation,
        "home_lineup": home_lineup,
        "away_lineup": away_lineup,
    }

    return render(request, "lineup_app/pitch_lineup.html", context)
