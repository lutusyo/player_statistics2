def get_technical_report_data(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    start = parse_date(request.GET.get("start_date", ""))
    end = parse_date(request.GET.get("end_date", ""))
    season = request.GET.get("season", "")

    results = Result.objects.filter(our_team=team)

    if start:
        results = results.filter(date__gte=start)
    if end:
        results = results.filter(date__lte=end)

    stats = get_statistics_report(
        filter_type=request.GET.get("filter", "all"),
        team=team,
        start_date=start,
        end_date=end,
    )

    return {
        "team": team,
        "start": start,
        "end": end,
        "season": season,
        "results": results.order_by("date"),
        "stats": stats,
    }