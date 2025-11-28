import pandas as pd
from django.db.models import Q
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
    """Convert value to float safely."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def safe_int(value):
    """Convert value to int safely."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return None



def match_player(full_name):
    """
    Intelligent matching of CSV player name to Player model.
    Handles:
    - 1, 2, or 3-part names
    - partial matches
    - swapped names
    - case-insensitive matching
    """

    full_name = full_name.strip().lower()
    parts = full_name.split()

    # --- 1. Match by exact full name in ANY order ---
    players = Player.objects.filter(
        Q(name__iexact=parts[0]) |
        Q(second_name__iexact=parts[0]) |
        Q(surname__iexact=parts[0]) |
        Q(name__icontains=full_name) |
        Q(second_name__icontains=full_name) |
        Q(surname__icontains=full_name)
    )

    if players.count() == 1:
        return players.first()

    # --- 2. Full name matching using name + surname ---
    if len(parts) >= 2:
        first = parts[0]
        last = parts[-1]

        players = Player.objects.filter(
            Q(name__iexact=first) & Q(surname__iexact=last)
        )

        if players.count() == 1:
            return players.first()

    # --- 3. Try matching ANY of the three name fields ---
    players = Player.objects.filter(
        Q(name__iexact=full_name) |
        Q(second_name__iexact=full_name) |
        Q(surname__iexact=full_name)
    )

    if players.count() == 1:
        return players.first()

    # --- 4. Fallback: partial match (most useful for Spiideo / Catapult names) ---
    players = Player.objects.filter(
        Q(name__icontains=parts[0]) |
        Q(surname__icontains=parts[0])
    )

    if players.count() == 1:
        return players.first()

    # Not found
    print(f"⚠️ No match found for '{full_name}'")
    return None




def import_gps_data(csv_file_path, match_id):
    """
    Imports GPS data from the CSV file into GPSRecord model.
    Correctly matches players using name, second_name, surname.
    """
    match = Match.objects.get(id=match_id)

    # Read CSV, skipping metadata rows
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

        # --- PLAYER MATCHING ---
        player_full_name = str(row.get("player_name", "")).strip()
        if not player_full_name:
            continue

        player = match_player(player_full_name)

        if not player:
            print(f"⚠️ Player not found in database → {player_full_name}")
            continue


        period = str(row.get("period_name", "")).strip()

        gps_record, created = GPSRecord.objects.update_or_create(
            match=match,
            player=player,
            period_name=period,
            defaults={
                "player_name": player_full_name,
                "period_number": safe_int(row.get("period_number")),
                "max_acceleration": safe_float(row.get("max_acceleration")),
                "max_deceleration": safe_float(row.get("max_deceleration")),
                "acceleration_efforts": safe_int(row.get("acceleration_efforts")),
                "deceleration_efforts": safe_int(row.get("deceleration_efforts")),
                "accel_decel_efforts": safe_int(row.get("accel_plus_decel_efforts")),
                "accel_decel_efforts_per_minute": safe_float(row.get("accel_plus_decel_efforts_per_minute")),
                "duration": hhmmss_to_minutes(row.get("duration")),
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
        print("Reading row for:", row["player_name"])
        print("Matched DB player:", player)


    print("✅ GPS data successfully imported (with correct player matching).")
