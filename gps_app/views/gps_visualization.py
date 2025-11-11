from django.shortcuts import render, get_object_or_404
from matches_app.models import Match
from gps_app.models import GPSRecord
from django.http import JsonResponse

def gps_dashboard(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    periods = ["Session", "First Half", "Second Half"]
    return render(request, "gps_app/gps_dashboard.html", {"match": match, "periods": periods})

def gps_dashboard_data(request, match_id):
    period = request.GET.get("period", "Session")
    match = get_object_or_404(Match, id=match_id)
    gps_records = GPSRecord.objects.filter(match=match, period_name=period)

    players = [r.player_name for r in gps_records]
    positions = [r.player.position for r in gps_records]  # <--- make sure GPSRecord has a related player with position
    distances = [r.distance or 0 for r in gps_records]
    accel_decel = [r.accel_decel_efforts or 0 for r in gps_records]
    sprint_efforts = [r.sprint_efforts or 0 for r in gps_records]
    high_speed = [r.high_speed_efforts or 0 for r in gps_records]
    walking_distance = [r.walking_distance or 0 for r in gps_records]

    data = {
        "players": players,
        "positions": positions,
        "distances": distances,
        "accel_decel": accel_decel,
        "sprint_efforts": sprint_efforts,
        "high_speed": high_speed,
        "walking_distance": walking_distance,
    }
    return JsonResponse(data)

