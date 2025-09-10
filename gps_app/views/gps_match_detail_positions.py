import csv
import json
from io import TextIOWrapper
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from gps_app.forms import GPSUploadForm
from gps_app.models import GPSRecord
from matches_app.models import Match
from lineup_app.models import MatchLineup, Substitution
from players_app.models import Player
from django.db.models import Count


def gps_position_detail(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    records = GPSRecord.objects.filter(match=match).select_related('player')

    # Aggregate example data
    total_distance = sum(r.distance for r in records)
    avg_max_velocity = sum(r.max_velocity for r in records) / records.count() if records.exists() else 0

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
        sum(r.max_velocity for r in records) / records.count() if records.exists() else 0,
        sum(r.sprint_distance for r in records) / records.count() if records.exists() else 0,
        sum(r.sprint_efforts for r in records) / records.count() if records.exists() else 0,
        sum(r.player_load for r in records) / records.count() if records.exists() else 0,
        sum(r.acceleration_efforts for r in records) / records.count() if records.exists() else 0,
        sum(r.deceleration_efforts for r in records) / records.count() if records.exists() else 0,
        sum(r.impacts or 0 for r in records) / records.count() if records.exists() else 0,
    ]

    # Filter records by position
    forwards = records.filter(player__position='Forward')
    midfielders = records.filter(player__position='Midfielder')
    defenders = records.filter(player__position='Defender')
    goalkeepers = records.filter(player__position='Goalkeeper')

    context = {
        'match': match,
        'records': records,
        'total_distance': total_distance,
        'avg_max_velocity': avg_max_velocity,
        'pie_labels': json.dumps(pie_labels),
        'pie_data': json.dumps(pie_data),
        'radar_labels': json.dumps(radar_labels),
        'radar_data': json.dumps(radar_data),
        'forwards': forwards,
        'midfielders': midfielders,
        'defenders': defenders,
        'goalkeepers': goalkeepers,
    }

    return render(request, 'gps_app/gps_position_detail.html', context)