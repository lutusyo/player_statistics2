from django.shortcuts import render, get_object_or_404
from matches_app.models import Match
from gps_app.models import GPSRecord
from django.http import JsonResponse

def gps_dashboard(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    periods = ["Session", "First Half", "Second Half"]
    positions = GPSRecord.objects.filter(match=match).values_list("player__position", flat=True).distinct()
    return render(request, "gps_app/gps_dashboard.html", {"match": match, "periods": periods, "positions": positions})

def gps_dashboard_data(request, match_id):
    period = request.GET.get("period", "Session")
    match = get_object_or_404(Match, id=match_id)
    gps_records = GPSRecord.objects.filter(match=match, period_name=period)

    players = [r.player_name for r in gps_records]
    positions = [r.player.position for r in gps_records]
    data = {
        "players": players,
        "positions": positions,
        "distances": [r.distance or 0 for r in gps_records],
        "accel_decel": [r.accel_decel_efforts or 0 for r in gps_records],
        "sprint_efforts": [r.sprint_efforts or 0 for r in gps_records],
        "high_speed": [r.high_speed_efforts or 0 for r in gps_records],
        "walking_distance": [r.walking_distance or 0 for r in gps_records],
        "jogging_distance": [r.jogging_distance or 0 for r in gps_records],
        "running_distance": [r.running_distance or 0 for r in gps_records],
        "high_speed_distance": [r.high_speed_distance or 0 for r in gps_records],
        "sprint_distance": [r.sprint_distance or 0 for r in gps_records],
    }
    return JsonResponse(data)
