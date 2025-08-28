# gps_app/utils.py
import json
from gps_app.models import GPSRecord

def get_gps_context(match):
    records = GPSRecord.objects.filter(match=match).select_related('player')

    total_distance = sum(r.distance or 0 for r in records)
    avg_max_velocity = sum(r.max_velocity or 0 for r in records) / records.count() if records.exists() else 0

    pie_labels = ['Standing', 'Walking', 'Jogging', 'Running', 'Sprinting']
    pie_data = [
        sum(r.standing_distance or 0 for r in records),
        sum(r.walking_distance or 0 for r in records),
        sum(r.jogging_distance or 0 for r in records),
        sum(r.running_distance or 0 for r in records),
        sum(r.sprint_distance or 0 for r in records),
    ]

    radar_labels = [
        'Max Velocity', 'Sprint Distance', 'Sprint Efforts', 'Player Load',
        'Acceleration Efforts', 'Deceleration Efforts', 'Impacts'
    ]
    radar_data = [
        sum(r.max_velocity or 0 for r in records) / records.count() if records.exists() else 0,
        sum(r.sprint_distance or 0 for r in records) / records.count() if records.exists() else 0,
        sum(r.sprint_efforts or 0 for r in records) / records.count() if records.exists() else 0,
        sum(r.player_load or 0 for r in records) / records.count() if records.exists() else 0,
        sum(r.acceleration_efforts or 0 for r in records) / records.count() if records.exists() else 0,
        sum(r.deceleration_efforts or 0 for r in records) / records.count() if records.exists() else 0,
        sum(r.impacts or 0 for r in records) / records.count() if records.exists() else 0,
    ]

    return {
        'match': match,  # ✅ this is crucial
        'records': records,
        'total_distance': total_distance,
        'avg_max_velocity': avg_max_velocity,
        'pie_labels': json.dumps(pie_labels),
        'pie_data': json.dumps(pie_data),
        'radar_labels': json.dumps(radar_labels),
        'radar_data': json.dumps(radar_data),
    }
