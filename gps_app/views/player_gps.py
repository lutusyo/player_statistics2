# gps_app/views/player_gps.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Max

from players_app.models import Player
from gps_app.models import GPSRecord
from lineup_app.models import MatchLineup
from matches_app.models import Match


@login_required
def player_gps_overview(request, player_id):
    player = get_object_or_404(Player, id=player_id)

    sessions = (
        GPSRecord.objects
        .filter(player=player)
        .values(
            "match_id",
            "match__date",
            "match__home_team__name",
            "match__away_team__name",
        )
        .annotate(
            minutes=Sum("duration"),
            distance=Sum("distance"),
            running_distance=Sum("running_distance"),
            hi_distance=Sum("hi_distance"),
            sprint_distance=Sum("sprint_distance"),
            max_velocity=Max("max_velocity"),
            player_load=Sum("player_load"),
        )
        .order_by("match__date")
    )

    # Attach opponent + minutes played
    session_rows = []
    for row in sessions:
        match = Match.objects.get(id=row["match_id"])

        # opponent logic
        if player.team == match.home_team:
            opponent = match.away_team.name
        else:
            opponent = match.home_team.name

        lineup = MatchLineup.objects.filter(
            match=match,
            player=player
        ).first()

        session_rows.append({
            **row,
            "opponent": opponent,
            "minutes_played": lineup.minutes_played if lineup else 0,
        })

    context = {
        "player": player,
        "session_rows": session_rows,
    }

    return render(request, "gps_app/player_gps_overview.html", context)
