import pandas as pd
from django.shortcuts import render, get_object_or_404
from version2.psychology_app_v2.models import Player, Assessment, AgeGroup
from django.db.models import Avg
import json


def player_detail(request, player_id):
    player = get_object_or_404(Player, id=player_id)

    # 👥 Players in same age group (team navigation)
    team_players = Player.objects.filter(
        age_group=player.age_group
    ).order_by('player_name')

    # 🎯 Filters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    compare_id = request.GET.get('compare')

    assessments = player.assessments.all().order_by('start_date')

    if start_date:
        assessments = assessments.filter(start_date__gte=start_date)

    if end_date:
        assessments = assessments.filter(end_date__lte=end_date)

    # 📈 Main player data
    dates = [a.start_date.strftime('%Y-%m-%d') for a in assessments if a.start_date]
    overall = [(a.overall or 0) * 100 for a in assessments]

    # 🆚 ALWAYS initialize BEFORE using
    compare_player = None
    compare_data = []
    compare_radar = None

    # 🆚 Comparison player
    if compare_id:
        compare_player = get_object_or_404(Player, id=compare_id)

        compare_assessments = compare_player.assessments.all().order_by('start_date')

        # Apply same filters to comparison player
        if start_date:
            compare_assessments = compare_assessments.filter(start_date__gte=start_date)

        if end_date:
            compare_assessments = compare_assessments.filter(end_date__lte=end_date)

        compare_data = [(a.overall or 0) * 100 for a in compare_assessments]

        # 🧠 Radar for comparison
        compare_stats = compare_assessments.aggregate(
            cognitive=Avg('cognitive_percent'),
            personality=Avg('personality_percent'),
            neuro=Avg('neuro_psychology_percent'),
            education=Avg('education_percent'),
        )

        compare_radar = [
            (compare_stats['cognitive'] or 0) * 100,
            (compare_stats['personality'] or 0) * 100,
            (compare_stats['neuro'] or 0) * 100,
            (compare_stats['education'] or 0) * 100,
        ]

    # 🔥 FIXED SCALE (AFTER compare_data exists)
    all_values = [v for v in overall if v is not None]

    if compare_data:
        all_values += [v for v in compare_data if v is not None]

    if all_values:
        y_min = max(min(all_values) - 5, 0)
        y_max = min(max(all_values) + 5, 100)
    else:
        y_min, y_max = 0, 100

    # 🧠 Radar chart (main player)
    radar_stats = assessments.aggregate(
        cognitive=Avg('cognitive_percent'),
        personality=Avg('personality_percent'),
        neuro=Avg('neuro_psychology_percent'),
        education=Avg('education_percent'),
    )

    context = {
        'player': player,
        'team_players': team_players,
        'assessments': assessments,
        'dates': json.dumps(dates),
        'overall': json.dumps(overall),
        'y_min': y_min,
        'y_max': y_max,
        'compare_player': compare_player,
        'compare_data': json.dumps(compare_data),
        'players': Player.objects.all(),

        'compare_radar': json.dumps(compare_radar) if compare_radar else None,

        'radar': json.dumps([
            (radar_stats['cognitive'] or 0) * 100,
            (radar_stats['personality'] or 0) * 100,
            (radar_stats['neuro'] or 0) * 100,
            (radar_stats['education'] or 0) * 100,
        ]),

        'start_date': start_date,
        'end_date': end_date,
    }

    return render(request, 'psychology_app_v2/player_detail.html', context)