import json
from datetime import datetime
from dateutil.relativedelta import relativedelta

from django.shortcuts import render, get_object_or_404
from django.db.models import Avg

from version2.psychology_app_v2.models import Player


def player_detail(request, player_id):
    player = get_object_or_404(Player, id=player_id)

    team_players = Player.objects.filter(
        age_group=player.age_group
    ).order_by('player_name')

    # 🎯 Filters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    compare_id = request.GET.get('compare')
    period = request.GET.get('period')
    metric = request.GET.get('metric', 'overall')

    assessments = player.assessments.all().order_by('start_date')

    # -----------------------------------
    # ✅ PERIOD FILTER
    # -----------------------------------
    if period:
        try:
            period = int(period)
            first = assessments.first()

            if first and first.start_date:
                start = first.start_date
                end = start + relativedelta(months=period * 2)

                assessments = assessments.filter(
                    start_date__gte=start,
                    end_date__lte=end
                )

                start_date = start
                end_date = end
        except:
            pass
    else:
        try:
            if start_date:
                start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
                assessments = assessments.filter(start_date__gte=start_date)

            if end_date:
                end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
                assessments = assessments.filter(end_date__lte=end_date)
        except:
            start_date = None
            end_date = None

    # -----------------------------------
    # ✅ METRIC FUNCTION
    # -----------------------------------
    def get_metric(a):
        if metric == "cognitive":
            return (a.cognitive_percent or 0) * 100
        elif metric == "personality":
            return (a.personality_percent or 0) * 100
        elif metric == "neuro":
            return (a.neuro_psychology_percent or 0) * 100
        elif metric == "education":
            return (a.education_percent or 0) * 100
        return (a.overall or 0) * 100

    # 📈 Main chart data
    dates = [a.start_date.strftime('%Y-%m-%d') for a in assessments if a.start_date]
    values = [get_metric(a) for a in assessments]

    # -----------------------------------
    # 🆚 COMPARE
    # -----------------------------------
    compare_player = None
    compare_data = []
    compare_radar = None

    if compare_id:
        compare_player = get_object_or_404(Player, id=compare_id)
        compare_assessments = compare_player.assessments.all().order_by('start_date')

        if start_date:
            compare_assessments = compare_assessments.filter(start_date__gte=start_date)
        if end_date:
            compare_assessments = compare_assessments.filter(end_date__lte=end_date)

        compare_data = [get_metric(a) for a in compare_assessments]

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

    # 📊 Scale
    all_values = values + compare_data
    if all_values:
        y_min = max(min(all_values) - 5, 0)
        y_max = min(max(all_values) + 5, 100)
    else:
        y_min, y_max = 0, 100

    # 🧠 Radar
    radar_stats = assessments.aggregate(
        cognitive=Avg('cognitive_percent'),
        personality=Avg('personality_percent'),
        neuro=Avg('neuro_psychology_percent'),
        education=Avg('education_percent'),
    )

    # 📊 BAR CHART FOR ALL PLAYERS (same age group)
    bar_labels = []
    bar_values = []

    for p in team_players:
        p_assessments = p.assessments.all()

        # apply SAME filters
        if start_date:
            p_assessments = p_assessments.filter(start_date__gte=start_date)
        if end_date:
            p_assessments = p_assessments.filter(end_date__lte=end_date)

        # get metric values
        p_values = [get_metric(a) for a in p_assessments]

        avg = sum(p_values) / len(p_values) if p_values else 0

        bar_labels.append(p.player_name)
        bar_values.append(round(avg, 1))


    context = {
        'player': player,
        'team_players': team_players,
        'assessments': assessments,
        'dates': json.dumps(dates),
        'values': json.dumps(values),
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


        'bar_labels': json.dumps(list(bar_labels)),
        'bar_values': json.dumps(list(bar_values)),


        'y_min': y_min,
        'y_max': y_max,
        'start_date': start_date,
        'end_date': end_date,
        'period': str(period) if period else "",
        'metric': metric,
    }

    return render(request, 'psychology_app_v2/player_detail.html', context)