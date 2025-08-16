import csv
import json
from io import TextIOWrapper
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from gps_app.forms import GPSUploadForm
from gps_app.models import GPSRecord
from matches_app.models import Match
from lineup_app.models import MatchLineup
from players_app.models import Player
from django.db.models import Count


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
                messages.error(
                    request,
                    f"'{required_column}' column not found in CSV. Found: {list(header_map.keys())}"
                )
                return redirect('gps_app:gps_upload')

            # CSV → model mapping
            csv_field_map = {
                "Player Name": "player_name",
                "Period Name": "period_name",
                "Period Number": "period_number",
                "Max Acceleration": "max_acceleration",
                "Max Deceleration": "max_deceleration",
                "Acceleration Efforts": "acceleration_efforts",
                "Deceleration Efforts": "deceleration_efforts",
                "Accel + Decel Efforts": "accel_decel_efforts",
                "Accel + Decel Efforts Per Minute": "accel_decel_efforts_per_minute",
                "Duration": "duration",
                "Distance": "distance",
                "Player Load": "player_load",
                "Max Velocity": "max_velocity",
                "Max Vel (% Max)": "max_vel_percent_max",
                "Meterage Per Minute": "meterage_per_minute",
                "Player Load Per Minute": "player_load_per_minute",
                "Work/Rest Ratio": "work_rest_ratio",
                "Max Heart Rate": "max_heart_rate",
                "Avg Heart Rate": "avg_heart_rate",
                "Max HR (% Max)": "max_hr_percent_max",
                "Avg HR (% Max)": "avg_hr_percent_max",
                "HR Exertion": "hr_exertion",
                "Red Zone": "red_zone",
                "Heart Rate Band 1 Duration": "heart_rate_band_1_duration",
                "Heart Rate Band 2 Duration": "heart_rate_band_2_duration",
                "Heart Rate Band 3 Duration": "heart_rate_band_3_duration",
                "Heart Rate Band 4 Duration": "heart_rate_band_4_duration",
                "Heart Rate Band 5 Duration": "heart_rate_band_5_duration",
                "Heart Rate Band 6 Duration": "heart_rate_band_6_duration",
                "Energy": "energy",
                "High Metabolic Load Distance": "high_metabolic_load_distance",
                "Standing Distance": "standing_distance",
                "Walking Distance": "walking_distance",
                "Jogging Distance": "jogging_distance",
                "Running Distance": "running_distance",
                "HI Distance": "hi_distance",
                "Sprint Distance": "sprint_distance",
                "Sprint Efforts": "sprint_efforts",
                "Sprint Dist Per Min": "sprint_dist_per_min",
                "High Speed Distance": "high_speed_distance",
                "High Speed Efforts": "high_speed_efforts",
                "High Speed Distance Per Minute": "high_speed_distance_per_minute",
                "Impacts": "impacts",
                "Athlete Tags": "athlete_tags",
                "Activity Tags": "activity_tags",
                "Game Tags": "game_tags",
                "Athlete Participation Tags": "athlete_participation_tags",
                "Period Tags": "period_tags",
            }

            created_count = 0
            for row in reader:
                if row[header_map["Period Name"]].strip() != "Session":
                    continue

                pod_number = row[header_map["Player Name"]].strip()
                lineup = MatchLineup.objects.filter(match=match, pod_number=pod_number).first()
                if not lineup:
                    print(f"⚠️ No lineup found for pod {pod_number} in match {match}")
                    continue

                if GPSRecord.objects.filter(match=match, lineup=lineup).exists():
                    print(f"⏭️ GPS data already exists for player {lineup.player.name} in this match.")
                    continue

                record_data = {}
                for csv_col, model_field in csv_field_map.items():
                    idx = header_map.get(csv_col)
                    if idx is not None and idx < len(row):
                        value = row[idx].strip()
                        # Convert numeric values
                        if value.replace('.', '', 1).isdigit():
                            if '.' in value:
                                value = float(value)
                            else:
                                value = int(value)
                        record_data[model_field] = value or None

                try:
                    GPSRecord.objects.create(
                        match=match,
                        player=lineup.player,
                        lineup=lineup,
                        **record_data
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