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



def gps_matches_list(request):
    # List matches with at least one GPS record, annotated with record counts
    matches = Match.objects.annotate(gps_count=Count('gps_records')).filter(gps_count__gt=0).order_by('-date')

    context = {
        'matches': matches,
    }
    return render(request, 'gps_app/gps_list.html', context)