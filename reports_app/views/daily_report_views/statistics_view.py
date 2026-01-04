from django.shortcuts import render, get_object_or_404
from django.db.models import Sum, Q
from django.utils.timezone import now
from datetime import timedelta
from players_app.models import Player
from lineup_app.models import MatchLineup
from tagging_app.models import AttemptToGoal
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from io import BytesIO
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from django.utils.dateparse import parse_date
from teams_app.models import Team
from reports_app.models import PlayerTrainingMinutes


# ====================== REPORT HELPER ======================
def get_statistics_report(filter_type="all", team=None, start_date=None, end_date=None):
    today = now().date()

    # Determine start date based on filter_type if no explicit start_date provided
    if not start_date:
        if filter_type == "week":
            start_date = today - timedelta(days=7)
        elif filter_type == "month":
            start_date = today.replace(day=1)

    # Match date filter
    match_filter = Q()
    if start_date:
        match_filter &= Q(match__date__gte=start_date)
    if end_date:
        match_filter &= Q(match__date__lte=end_date)

    report = []

    players = Player.objects.filter(is_active=True, team=team)

    for player in players:
        lineups = MatchLineup.objects.filter(player=player).filter(match_filter)

        appearances = lineups.count()
        starts = lineups.filter(is_starting=True).count()
        sub_in = lineups.filter(is_starting=False, time_in__isnull=False).count()
        sub_out = lineups.filter(time_out__isnull=False).count()
        game_minutes = lineups.aggregate(total=Sum('minutes_played'))['total'] or 0

        goals = AttemptToGoal.objects.filter(
            player=player, outcome='On Target Goal'
        ).filter(match_filter).count()

        assists = AttemptToGoal.objects.filter(
            assist_by=player, outcome='On Target Goal'
        ).filter(match_filter).count()

        # Training minutes
        training_minutes_qs = PlayerTrainingMinutes.objects.filter(
            player=player, training_session__team=team
        )
        if start_date:
            training_minutes_qs = training_minutes_qs.filter(training_session__date__gte=start_date)
        if end_date:
            training_minutes_qs = training_minutes_qs.filter(training_session__date__lte=end_date)

        training_minutes = training_minutes_qs.aggregate(total=Sum('minutes'))['total'] or 0

        report.append({
            "player": player,
            "position": player.position,
            "training_minutes": training_minutes,
            "game_minutes": game_minutes,
            "appearances": appearances,
            "starts": starts,
            "sub_in": sub_in,
            "sub_out": sub_out,
            "goals": goals,
            "assists": assists,
            "note": "",
        })

    return report


# ====================== NORMAL VIEW ======================
@login_required
def statistics_list_view(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    filter_type = request.GET.get("filter", "all")

    # Parse start/end dates from GET parameters
    start_date_str = request.GET.get("start_date")
    end_date_str = request.GET.get("end_date")
    start_date = parse_date(start_date_str) if start_date_str else None
    end_date = parse_date(end_date_str) if end_date_str else None

    report = get_statistics_report(
        filter_type=filter_type,
        team=team,
        start_date=start_date,
        end_date=end_date
    )

    context = {
        "report": report,
        "filter_type": filter_type,
        "team": team,
        "start_date": start_date_str,
        "end_date": end_date_str,
    }
    return render(request, "reports_app/daily_report_templates/9statistics/statistics_list.html", context)


# ====================== EXPORT TO EXCEL ======================
@login_required
def statistics_export_excel(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    filter_type = request.GET.get("filter", "all")
    start_date = parse_date(request.GET.get("start_date"))
    end_date = parse_date(request.GET.get("end_date"))

    report = get_statistics_report(
        filter_type=filter_type,
        team=team,
        start_date=start_date,
        end_date=end_date
    )

    df = pd.DataFrame([{
        "Name": r["player"].name,
        "Position": r["position"],
        "Training Minutes": r["training_minutes"],
        "Game Minutes": r["game_minutes"],
        "Appearances": r["appearances"],
        "Starts": r["starts"],
        "Sub In": r["sub_in"],
        "Sub Out": r["sub_out"],
        "Goals": r["goals"],
        "Assists": r["assists"],
        "Note": r["note"],
    } for r in report])

    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Player Stats")

    response = HttpResponse(
        output.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    filename = f"Player_Stats_{team.age_group.code}.xlsx"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


# ====================== EXPORT TO PDF ======================
@login_required
def statistics_export_pdf(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    filter_type = request.GET.get("filter", "all")
    start_date = parse_date(request.GET.get("start_date"))
    end_date = parse_date(request.GET.get("end_date"))

    report = get_statistics_report(
        filter_type=filter_type,
        team=team,
        start_date=start_date,
        end_date=end_date
    )

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()

    data = [["Name", "Pos", "Train", "Game", "Apps", "Starts", "In", "Out", "Goals", "Ast", "Note"]]
    for r in report:
        data.append([
            r["player"].name, r["position"], r["training_minutes"], r["game_minutes"],
            r["appearances"], r["starts"], r["sub_in"], r["sub_out"],
            r["goals"], r["assists"], r["note"]
        ])

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))

    doc.build([Paragraph("Player Statistics Report", styles["Heading2"]), table])
    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="player_stats.pdf"'
    response.write(pdf)
    return response
