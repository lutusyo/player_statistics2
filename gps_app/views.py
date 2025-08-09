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

            # Skip metadata rows (typically first 9)
            for _ in range(9):
                next(reader, None)

            headers = next(reader, None)
            if not headers:
                messages.error(request, "CSV header row missing.")
                return redirect('gps_app:gps_upload')

            header_map = {h.strip().strip('"'): i for i, h in enumerate(headers)}
            required_column = "Period Name"

            if required_column not in header_map:
                messages.error(request, f"'{required_column}' column not found in CSV. Found: {list(header_map.keys())}")
                return redirect('gps_app:gps_upload')

            created_count = 0
            for row in reader:
                if row[header_map["Period Name"]].strip() != "Session":
                    continue

                pod_number = row[header_map["Player Name"]].strip()
                lineup = MatchLineup.objects.filter(match=match, pod_number=pod_number).first()
                if not lineup:
                    print(f"⚠️  No lineup found for pod {pod_number} in match {match}")
                    continue

                if GPSRecord.objects.filter(match=match, lineup=lineup).exists():
                    print(f"⏭️  GPS data already exists for player {lineup.player.name} in this match.")
                    continue

                def get_float(col): return float(row[header_map.get(col, -1)] or 0) if col in header_map else 0
                def get_int(col): return int(row[header_map.get(col, -1)] or 0) if col in header_map else 0

                try:
                    
                    duration = row[header_map.get("Duration", -1)].strip() if "Duration" in header_map else "00:00:00"
                    
                    GPSRecord.objects.create(
                        match=match,
                        player=lineup.player,
                        lineup=lineup,
                        duration=duration,
                        max_velocity=get_float("Max Velocity"),
                        max_acceleration=get_float("Max Acceleration"),
                        max_deceleration=get_float("Max Deceleration"),
                        acceleration_efforts=get_int("Acceleration Efforts"),
                        deceleration_efforts=get_int("Deceleration Efforts"),
                        distance=get_float("Distance"),
                        player_load=get_float("Player Load"),
                        meterage_per_minute=get_float("Meterage Per Minute"),
                        player_load_per_minute=get_float("Player Load Per Minute"),
                        max_heart_rate=get_float("Max Heart Rate"),
                        avg_heart_rate=get_float("Avg Heart Rate"),
                        sprint_distance=get_float("Sprint Distance"),
                        sprint_efforts=get_int("Sprint Efforts"),
                        jogging_distance=get_float("Jogging Distance"),
                        walking_distance=get_float("Walking Distance"),
                        high_speed_distance=get_float("High Speed Distance"),
                        high_speed_efforts=get_int("High Speed Efforts"),
                        impacts=get_int("Impacts"),
                    )
                    created_count += 1
                except Exception as e:
                    messages.error(request, f"❌ Error processing pod {pod_number}: {str(e)}")
                    continue

            messages.success(request, f"✅ GPS data uploaded successfully. {created_count} records created.")
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

    pie_labels = ['Jogging', 'Walking', 'High Speed']
    pie_data = [
        sum(r.jogging_distance for r in records),
        sum(r.walking_distance for r in records),
        sum(r.high_speed_distance for r in records),
    ]

    radar_labels = ['Max Velocity', 'Sprint Distance', 'Efforts', 'Player Load']
    radar_data = [
        sum(r.max_velocity for r in records) / len(records) if records else 0,
        sum(r.sprint_distance for r in records) / len(records) if records else 0,
        sum(r.sprint_efforts for r in records) / len(records) if records else 0,
        sum(r.player_load for r in records) / len(records) if records else 0,
    ]

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
