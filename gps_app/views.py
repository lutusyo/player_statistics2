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

from django.db.models import Count

def gps_matches_list(request):
    # List matches with at least one GPS record, annotated with record counts
    matches = Match.objects.annotate(gps_count=Count('gps_records')).filter(gps_count__gt=0).order_by('-date')

    context = {
        'matches': matches,
    }
    return render(request, 'gps_app/gps_list.html', context)



def gps_match_detail(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    records = GPSRecord.objects.filter(match=match).select_related('player')

    # Example of data aggregation: total distance, average heart rates, etc.
    total_distance = sum(r.distance for r in records)
    avg_max_velocity = sum(r.max_velocity for r in records) / records.count() if records.exists() else 0

    # Prepare JSON data for charts (adapt fields as needed)
    pie_labels = ['Standing', 'Walking', 'Jogging', 'Running', 'Sprinting']
    pie_data = [
        sum(r.standing_distance or 0 for r in records),
        sum(r.walking_distance or 0 for r in records),
        sum(r.jogging_distance or 0 for r in records),
        sum(r.running_distance or 0 for r in records),
        sum(r.sprinting_distance or 0 for r in records),
    ]

    radar_labels = [
        'Max Velocity', 'Sprint Distance', 'Sprint Efforts', 'Player Load',
        'Acceleration Efforts', 'Deceleration Efforts', 'Impacts'
    ]
    radar_data = [
        sum(r.max_velocity for r in records) / records.count() if records.exists() else 0,
        sum(r.sprint_distance for r in records) / records.count() if records.exists() else 0,
        sum(r.sprint_efforts for r in records) / records.count() if records.exists() else 0,
        sum(r.player_load for r in records) / records.count() if records.exists() else 0,
        sum(r.acceleration_efforts for r in records) / records.count() if records.exists() else 0,
        sum(r.deceleration_efforts for r in records) / records.count() if records.exists() else 0,
        sum(r.impacts or 0 for r in records) / records.count() if records.exists() else 0,
    ]

    context = {
        'match': match,
        'records': records,
        'total_distance': total_distance,
        'avg_max_velocity': avg_max_velocity,
        'pie_labels': json.dumps(pie_labels),
        'pie_data': json.dumps(pie_data),
        'radar_labels': json.dumps(radar_labels),
        'radar_data': json.dumps(radar_data),
    }
    return render(request, 'gps_app/gps_match_detail.html', context)
