from django.shortcuts import render, get_object_or_404
from matches_app.models import Match
from lineup_app.models import MatchLineup, POSITION_COORDS, Substitution
from players_app.models import Player
from teams_app.models import Team

def both_teams_lineup_view(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    lineups = MatchLineup.objects.filter(match=match).select_related("player", "team")

    # ✅ STEP 1: Ensure opponent players exist
    opponent_team = Team.objects.filter(team_type="OPPONENT_TEAM").first()
    if opponent_team:
        existing_opponent_players = Player.objects.filter(team=opponent_team).count()
        if existing_opponent_players < 22:
            # Create missing opponent players (Player 1 ... Player 22)
            for i in range(existing_opponent_players + 1, 23):
                Player.objects.create(
                    name=f"Player {i}",
                    jersey_number=i,
                    team=opponent_team
                )

        # ✅ STEP 2: Ensure lineup records exist for those players in this match
        opponent_players = Player.objects.filter(team=opponent_team)
        for p in opponent_players:
            if not MatchLineup.objects.filter(match=match, team=opponent_team, player=p).exists():
                MatchLineup.objects.create(
                    match=match,
                    team=opponent_team,
                    player=p,
                    is_starting=False,  # default to subs
                    position="SUB",
                    formation="4-4-2"
                )

    # ✅ STEP 3: Now continue with your existing logic
    lineups = MatchLineup.objects.filter(match=match).select_related("player", "team")

    our_team_lineup, opponent_team_lineup, our_subs, opponent_subs = [], [], [], []

    our_team_formation = (
        lineups.filter(team__team_type="OUR_TEAM", is_starting=True)
        .values_list("formation", flat=True)
        .first()
        or "4-4-2"
    )
    opponent_formation = (
        lineups.filter(team__team_type="OPPONENT_TEAM", is_starting=True)
        .values_list("formation", flat=True)
        .first()
        or "4-4-2"
    )

    def get_coords(formation, position):
        formation_map = POSITION_COORDS.get(formation, {})
        if position in formation_map:
            return formation_map[position]

        fallback_map = {
            "ST": ["ST1", "ST2"],
            "CM": ["LCM", "RCM", "CM"],
            "CB": ["LCB", "RCB", "CB"],
            "RM": ["RW", "RCM"],
            "LM": ["LW", "LCM"],
        }
        for alias in fallback_map.get(position, []):
            if alias in formation_map:
                return formation_map[alias]
        return {"top": 50, "left": 50}

    for l in lineups:
        player_info = {
            "id": l.id,
            "name": l.player.name,
            "number": l.player.jersey_number,
            "position": l.position,
            "photo": l.player.photo.url if l.player.photo else None,
        }

        if l.is_starting:
            if l.team.team_type == "OUR_TEAM":
                coords = get_coords(our_team_formation, l.position)
                player_info.update(coords)
                our_team_lineup.append(player_info)
            else:
                coords = get_coords(opponent_formation, l.position)
                player_info.update(coords)
                opponent_team_lineup.append(player_info)
        else:
            if l.team.team_type == "OUR_TEAM":
                our_subs.append(player_info)
            else:
                opponent_subs.append(player_info)

    substitutions = Substitution.objects.filter(match=match).select_related("player_out__player", "player_in__player")

    context = {
        "match": match,
        "our_team_lineup": our_team_lineup,
        "opponent_team_lineup": opponent_team_lineup,
        "our_subs": our_subs,
        "opponent_subs": opponent_subs,
        "substitutions": substitutions,
        "our_team_formation": our_team_formation,
        "opponent_formation": opponent_formation,
    }

    return render(request, "lineup_app/both_teams_lineup.html", context)
