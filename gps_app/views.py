import csv
import json
from io import TextIOWrapper
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import GPSUploadForm
from .models import GPSRecord
from matches_app.models import Match, MatchLineup
from players_app.models import Player

def upload_gps_data(request):
    if request.method == 'POST':
        form = GPSUploadForm(request.POST, request.FILES)
        if form.is_valid():
            match = form.cleaned_data['match']
            file = TextIOWrapper(request.FILES['csv_file'].file, encoding='utf-8')
            reader = csv.reader(file)

            # Skip metadata rows (first 9 rows)
            for _ in range(9):
                next(reader)

            headers = next(reader)
            header_map = {h.strip().strip('"'): i for i, h in enumerate(headers)}

            required_column = "Period Name"
            if required_column not in header_map:
                messages.error(request, f"'{required_column}' column not found in CSV. Found: {list(header_map.keys())}")
                return redirect('gps_app:gps_upload')

            for row in reader:
                if row[header_map["Period Name"]].strip() != "Session":
                    continue

                pod_number = row[header_map["Player Name"]].strip()

                try:
                    lineup = MatchLineup.objects.get(match=match, pod_number=pod_number)
                    player = lineup.player
                except MatchLineup.DoesNotExist:
                    messages.warning(request, f"Pod '{pod_number}' not assigned to any player for this match.")
                    continue

                try:
                    GPSRecord.objects.create(
                        match=match,
                        player=player,
                        pod_number=pod_number,
                        max_velocity=float(row[header_map.get("Max Velocity", 0)] or 0),
                        max_acceleration=float(row[header_map.get("Max Acceleration", 0)] or 0),
                        max_deceleration=float(row[header_map.get("Max Deceleration", 0)] or 0),
                        acceleration_efforts=int(row[header_map.get("Acceleration Efforts", 0)] or 0),
                        deceleration_efforts=int(row[header_map.get("Deceleration Efforts", 0)] or 0),
                        #duration=float(row[header_map.get("Duration", 0
                        distance=float(row[header_map.get("Distance", 0)] or 0),
                        player_load=float(row[header_map.get("Player Load", 0)] or 0),
                        meterage_per_minute=float(row[header_map.get("Meterage Per Minute", 0)] or 0),
                        player_load_per_minute=float(row[header_map.get("Player Load Per Minute", 0)] or 0),
                        max_heart_rate=float(row[header_map.get("Max Heart Rate", 0)] or 0),
                        avg_heart_rate=float(row[header_map.get("Avg Heart Rate", 0)] or 0),
                        sprint_distance=float(row[header_map.get("Sprint Distance", 0)] or 0),
                        sprint_efforts=int(row[header_map.get("Sprint Efforts", 0)] or 0),
                        jogging_distance=float(row[header_map.get("Jogging Distance", 0)] or 0),
                        walking_distance=float(row[header_map.get("Walking Distance", 0)] or 0),
                        high_speed_distance=float(row[header_map.get("High Speed Distance", 0)] or 0),
                        high_speed_efforts=int(row[header_map.get("High Speed Efforts", 0)] or 0),
                        impacts=int(row[header_map.get("Impacts", 0)] or 0),
                    )
                except Exception as e:
                    messages.error(request, f"Error processing row for pod {pod_number}: {str(e)}")
                    continue

            messages.success(request, "GPS data uploaded successfully.")
            return redirect('gps_app:gps_dashboard')
    else:
        form = GPSUploadForm()

    return render(request, 'gps_app/gps_upload.html', {'form': form})



def gps_dashboard(request):
    records = GPSRecord.objects.all()

    player_filter = request.GET.get('player')
    match_filter = request.GET.get('match')

    if player_filter:
        records = records.filter(player__id=player_filter)
    if match_filter:
        records = records.filter(match__id=match_filter)

    # Pie Data (movement distances)
    pie_labels = ['Jogging', 'Walking', 'High Speed']
    pie_data = [
        sum(r.jogging_distance for r in records),
        sum(r.walking_distance for r in records),
        sum(r.high_speed_distance for r in records),
    ]

    # Radar Data (averaged performance metrics)
    radar_labels = ['Max Velocity', 'Sprint Distance', 'Efforts', 'Player Load']
    radar_data = [
        sum(r.max_velocity for r in records) / len(records) if records else 0,
        sum(r.sprint_distance for r in records) / len(records) if records else 0,
        sum(r.sprint_efforts for r in records) / len(records) if records else 0,
        sum(r.player_load for r in records) / len(records) if records else 0,
    ]

    # Trend Data: Sprint Distance over Time
    trend_data = {}
    for r in records:
        date = r.match.date.strftime('%Y-%m-%d')
        trend_data[date] = trend_data.get(date, 0) + r.sprint_distance

    trend_labels = list(trend_data.keys())
    trend_values = list(trend_data.values())

    context = {
        'records': records,
        'pie_labels': json.dumps(pie_labels),
        'pie_data': json.dumps(pie_data),
        'radar_labels': json.dumps(radar_labels),
        'radar_data': json.dumps(radar_data),
        'trend_labels': json.dumps(trend_labels),
        'trend_values': json.dumps(trend_values),
        'players': Player.objects.all(),
        'matches': Match.objects.all(),
    }
    return render(request, 'gps_app/gps_dashboard.html', context)


def gps_match_detail(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    records = GPSRecord.objects.filter(match=match)

    context = {
        'match': match,
        'records': records,
    }
    return render(request, 'gps_app/gps_match_detail.html', context)

