# gps_app/views/player_gps.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from players_app.models import Player
from gps_app.models import GPSRecord
from matches_app.models import Match

@login_required
def player_gps_overview(request, player_id):
    player = get_object_or_404(Player, id=player_id)

    gps_records = (GPSRecord.objects.filter(player=player).select_related("match").order_by("-match__date", "period_number"))

    #Group GPS data by match
    match_data = {}
    for record in gps_records:
        match = record.match
        if match not in match_data:
            match_data[match] = []
        match_data[match].append(record)

    context = {
        "player": player,
        "match_data": match_data,
    }

    return render(request, "gps_app/player_gps_overview.html", context)
