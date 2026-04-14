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

    # 🔥 Fix scale issue (dynamic min/max)
    all_values = [v for v in overall if v is not None]
    y_min = min(all_values) - 5 if all_values else 0
    y_max = max(all_values) + 5 if all_values else 100

    # 🆚 Comparison player
    compare_player = None
    compare_data = []

    if compare_id:
        compare_player = Player.objects.get(id=compare_id)
        compare_assessments = compare_player.assessments.all().order_by('start_date')

        compare_data = [(a.overall or 0) * 100 for a in compare_assessments]

    # 🧠 Radar chart (average scores)
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
        'players': Player.objects.all(),  # for dropdown

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