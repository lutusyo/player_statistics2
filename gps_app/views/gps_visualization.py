from django.shortcuts import render, get_object_or_404
from matches_app.models import Match
from gps_app.models import GPSRecord
from django.http import JsonResponse

from lineup_app.models import MatchLineup

def gps_dashboard(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    periods = ["Session", "First Half", "Second Half"]
    positions = GPSRecord.objects.filter(match=match).values_list("player__position", flat=True).distinct()
    return render(request, "gps_app/gps_dashboard.html", {"match": match, "periods": periods, "positions": positions})

def gps_dashboard_data(request, match_id):
    period = request.GET.get("period", "Session")
    match = get_object_or_404(Match, id=match_id)

    gps_records = GPSRecord.objects.select_related("player").filter(
        match=match,
        period_name=period
    )

    minutes_map = {
        ml.player_id: ml.minutes_played
        for ml in MatchLineup.objects.filter(match=match)
    }

    data = {
        "players": [],
        "minutes": [],
        "positions": [],
        "distances": [],
        "accel_decel": [],
        "sprint_efforts": [],
        "high_speed": [],
        "walking_distance": [],
        "jogging_distance": [],
        "running_distance": [],
        "high_speed_distance": [],
        "sprint_distance": [],
    }

    for r in gps_records:
        player_id = r.player_id

        data["players"].append(r.player_name or r.player.name)
        data["minutes"].append(minutes_map.get(player_id, 0))
        data["positions"].append(r.player.position)
        data["distances"].append(r.distance or 0)
        data["accel_decel"].append(r.accel_decel_efforts or 0)
        data["sprint_efforts"].append(r.sprint_efforts or 0)
        data["high_speed"].append(r.high_speed_efforts or 0)
        data["walking_distance"].append(r.walking_distance or 0)
        data["jogging_distance"].append(r.jogging_distance or 0)
        data["running_distance"].append(r.running_distance or 0)
        data["high_speed_distance"].append(r.high_speed_distance or 0)
        data["sprint_distance"].append(r.sprint_distance or 0)

    return JsonResponse(data)

