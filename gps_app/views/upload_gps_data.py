import pandas as pd
from io import TextIOWrapper
from django.shortcuts import render, redirect
from django.contrib import messages
from gps_app.forms import GPSUploadForm
from gps_app.models import GPSRecord
from matches_app.models import Match
from lineup_app.models import MatchLineup


def upload_gps_data(request):
    if request.method == 'POST':
        form = GPSUploadForm(request.POST, request.FILES)
        if form.is_valid():
            match = form.cleaned_data['match']

            # Wrap uploaded file so pandas can read it
            file = TextIOWrapper(request.FILES['csv_file'].file, encoding='utf-8')

            try:
                # Use pandas with sep=None to auto-detect delimiter (comma, tab, semicolon, etc.)
                # Skip first 9 metadata rows (common in GPS exports)
                df = pd.read_csv(file, sep=None, engine="python", skiprows=9)

            except Exception as e:
                messages.error(request, f"❌ Error reading CSV file: {str(e)}")
                return redirect('gps_app:gps_upload')

            # Ensure required column exists
            required_column = "Period Name"
            if required_column not in df.columns:
                messages.error(
                    request,
                    f"'{required_column}' column not found in CSV. Found: {list(df.columns)}"
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

            # Iterate through dataframe rows instead of csv.reader
            for _, row in df.iterrows():
                period_val = str(row.get("Period Name", "")).strip()
                print(f"Row Period Name = '{period_val}'")  # debug

                # Only keep rows where "Period Name" == "Session" (case-insensitive)
                if period_val.lower() != "session":
                    continue

                pod_number = str(row.get("Player Name", "")).strip()
                lineup = MatchLineup.objects.filter(match=match, pod_number=pod_number).first()
                if not lineup:
                    print(f"⚠️ No lineup found for pod {pod_number} in match {match}")
                    continue

                if GPSRecord.objects.filter(match=match, lineup=lineup).exists():
                    print(f"⏭️ GPS data already exists for player {lineup.player.name} in this match.")
                    continue

                record_data = {}
                for csv_col, model_field in csv_field_map.items():
                    if csv_col in df.columns:
                        value = str(row[csv_col]).strip()
                        if value == "" or value.lower() == "nan":
                            value = None
                        else:
                            try:
                                if "." in value:
                                    value = float(value)
                                else:
                                    value = int(value)
                            except ValueError:
                                pass
                        record_data[model_field] = value

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
