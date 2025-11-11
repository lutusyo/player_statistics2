import pandas as pd
from gps_app.models import GPSRecord
from players_app.models import Player
from matches_app.models import Match

def hhmmss_to_minutes(hhmmss):
    """Convert HH:MM:SS string to total minutes as float."""
    if pd.isna(hhmmss):
        return None
    try:
        h, m, s = map(int, str(hhmmss).split(":"))
        return h * 60 + m + s / 60
    except:
        return None

def safe_float(value):
    """Convert value to float safely, return None if fails."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

def safe_int(value):
    """Convert value to int safely, return None if fails."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return None

def import_gps_data(csv_file_path, match_id):
    """
    Imports GPS data from the new CSV format into GPSRecord model.

    Args:
        csv_file_path: Path to the uploaded CSV file
        match_id: The match to associate records with
    """
    match = Match.objects.get(id=match_id)

    # Read CSV, skip metadata rows
    df = pd.read_csv(csv_file_path, skiprows=9)

    # Clean column names
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("(%_max)", "percent_max", regex=False)
        .str.replace("+", "plus")
        .str.replace("/", "_")
    )

    for _, row in df.iterrows():
        player_name = str(row.get("player_name", "")).strip()
        if not player_name:
            continue

        player, _ = Player.objects.get_or_create(name=player_name)
        period = str(row.get("period_name", "")).strip()

        gps_record, created = GPSRecord.objects.update_or_create(
            match=match,
            player=player,
            period_name=period,
            defaults={
                "player_name": player_name,
                "period_number": safe_int(row.get("period_number")),
                "max_acceleration": safe_float(row.get("max_acceleration")),
                "max_deceleration": safe_float(row.get("max_deceleration")),
                "acceleration_efforts": safe_int(row.get("acceleration_efforts")),
                "deceleration_efforts": safe_int(row.get("deceleration_efforts")),
                "accel_decel_efforts": safe_int(row.get("accel_plus_decel_efforts")),
                "accel_decel_efforts_per_minute": safe_float(row.get("accel_plus_decel_efforts_per_minute")),
                "duration": hhmmss_to_minutes(row.get("duration")),  # convert HH:MM:SS
                "distance": safe_float(row.get("distance")),
                "player_load": safe_float(row.get("player_load")),
                "max_velocity": safe_float(row.get("max_velocity")),
                "max_vel_percent_max": safe_float(row.get("max_vel_percent_max")),
                "meterage_per_minute": safe_float(row.get("meterage_per_minute")),
                "player_load_per_minute": safe_float(row.get("player_load_per_minute")),
                "work_rest_ratio": safe_float(row.get("work_rest_ratio")),
                "max_heart_rate": safe_float(row.get("max_heart_rate")),
                "avg_heart_rate": safe_float(row.get("avg_heart_rate")),
                "max_hr_percent_max": safe_float(row.get("max_hr_percent_max")),
                "avg_hr_percent_max": safe_float(row.get("avg_hr_percent_max")),
                "hr_exertion": safe_float(row.get("hr_exertion")),
                "red_zone": safe_float(row.get("red_zone")),
                "heart_rate_band_1_duration": hhmmss_to_minutes(row.get("heart_rate_band_1_duration")),
                "heart_rate_band_2_duration": hhmmss_to_minutes(row.get("heart_rate_band_2_duration")),
                "heart_rate_band_3_duration": hhmmss_to_minutes(row.get("heart_rate_band_3_duration")),
                "heart_rate_band_4_duration": hhmmss_to_minutes(row.get("heart_rate_band_4_duration")),
                "heart_rate_band_5_duration": hhmmss_to_minutes(row.get("heart_rate_band_5_duration")),
                "heart_rate_band_6_duration": hhmmss_to_minutes(row.get("heart_rate_band_6_duration")),
                "energy": safe_float(row.get("energy")),
                "high_metabolic_load_distance": safe_float(row.get("high_metabolic_load_distance")),
                "standing_distance": safe_float(row.get("standing_distance")),
                "walking_distance": safe_float(row.get("walking_distance")),
                "jogging_distance": safe_float(row.get("jogging_distance")),
                "running_distance": safe_float(row.get("running_distance")),
                "hi_distance": safe_float(row.get("hi_distance")),
                "sprint_distance": safe_float(row.get("sprint_distance")),
                "sprint_efforts": safe_int(row.get("sprint_efforts")),
                "sprint_dist_per_min": safe_float(row.get("sprint_dist_per_min")),
                "high_speed_distance": safe_float(row.get("high_speed_distance")),
                "high_speed_efforts": safe_int(row.get("high_speed_efforts")),
                "high_speed_distance_per_minute": safe_float(row.get("high_speed_distance_per_minute")),
                "impacts": safe_int(row.get("impacts")),
                "athlete_tags": row.get("athlete_tags"),
                "activity_tags": row.get("activity_tags"),
                "game_tags": row.get("game_tags"),
                "athlete_participation_tags": row.get("athlete_participation_tags"),
                "period_tags": row.get("period_tags"),
            },
        )

    print("✅ GPS data successfully imported.")
