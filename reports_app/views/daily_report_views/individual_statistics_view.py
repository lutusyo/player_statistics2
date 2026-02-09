from lineup_app.models import MatchLineup
from tagging_app.models import AttemptToGoal
from django.utils.timezone import now
from django.utils.dateparse import parse_date
from datetime import timedelta
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from players_app.models import Player
import json
from django.http import HttpResponse, Http404

from django.utils import timezone
from django.template.loader import render_to_string, get_template
from django.db.models import Q
from io import BytesIO
import datetime
import calendar
from matches_app.models import Match
from teams_app.models import Team
import pandas as pd

# ReportLab imports (for PDF export)
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet



def get_individual_player_report(player, filter_type="all", start_date=None, end_date=None):
    today = now().date()

    if not start_date:
        if filter_type == "week":
            start_date = today - timedelta(days=7)
        elif filter_type == "month":
            start_date = today.replace(day=1)

    match_filter = Q(player=player)

    if start_date:
        match_filter &= Q(match__date__gte=start_date)
    if end_date:
        match_filter &= Q(match__date__lte=end_date)

    lineups = ( MatchLineup.objects.filter(match_filter).select_related("match").order_by("match__date"))

    report = []

    for idx, lineup in enumerate(lineups, start=1):
        match = lineup.match
        goals = AttemptToGoal.objects.filter(match=match, player=player, outcome="On Target Goal").count()
        assists = AttemptToGoal.objects.filter(match=match, assist_by=player, outcome="On Target Goal").count()

        report.append({
            "match_no": idx,
            "date": match.date,
            "minutes": lineup.minutes_played or 0,
            "appearance": 1,
            "goals": goals,
            "assists": assists,
        })

    return report


def get_player_summary(player, report):
    return {
        "name": player.name,
        "position": player.position,
        "team": player.team.name,
        "appearances": len(report),
        "minutes": sum(r["minutes"] for r in report),
        "goals": sum(r["goals"] for r in report),
        "assists": sum(r["assists"] for r in report),
    }



@login_required
def player_report_view(request, player_id):
    player = get_object_or_404(Player, id=player_id)

    filter_type = request.GET.get("filter", "all")


    start_date_str = request.GET.get("start_date")
    end_date_str = request.GET.get("end_date")

    start_date = parse_date(start_date_str) if start_date_str else None
    end_date = parse_date(end_date_str) if end_date_str else None


    report = get_individual_player_report(
        player=player,
        filter_type=filter_type,
        start_date=start_date,
        end_date=end_date
    )

    summary = get_player_summary(player, report)

    labels = [r["date"].strftime("%Y-%m-%d") for r in report]
    goals = [r["goals"] for r in report]
    assists = [r["assists"] for r in report]




    context = {
        "player": player,
        "summary": summary,
        "report": report,
        "filter_type": filter_type,
        "start_date": start_date,
        "end_date": end_date,
        "labels_json": json.dumps([r["match_no"] for r in report]),
        "goals_json": json.dumps([r["goals"] for r in report]),
        "assists_json": json.dumps([r["assists"] for r in report]),
        "minutes_json": json.dumps([r["minutes"] for r in report]),
    }




    return render(request, "reports_app/daily_report_templates/9statistics/player_report.html", context)






@login_required
def player_report_export_excel(request, player_id):
    player = get_object_or_404(Player, id=player_id)

    filter_type = request.GET.get("filter", "all")

    start_date_str = request.GET.get("start_date")
    end_date_str = request.GET.get("end_date")

    start_date = parse_date(start_date_str) if start_date_str else None
    end_date = parse_date(end_date_str) if end_date_str else None

    report = get_individual_player_report(
        player=player,
        filter_type=filter_type,
        start_date=start_date,
        end_date=end_date,
    )

    df = pd.DataFrame(report)

    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Match Report")

    response = HttpResponse(
        output.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = (
        f'attachment; filename="{player.name}_report.xlsx"'
    )
    return response





@login_required
def player_report_export_pdf(request, player_id):
    player = get_object_or_404(Player, id=player_id)

    

    filter_type = request.GET.get("filter", "all")

    start_date_str = request.GET.get("start_date")
    end_date_str = request.GET.get("end_date")

    start_date = parse_date(start_date_str) if start_date_str else None
    end_date = parse_date(end_date_str) if end_date_str else None


    report = get_individual_player_report(
        player=player,
        filter_type=filter_type,
        start_date=start_date,
        end_date=end_date
    )

    # ---- SUMMARY ----
    appearances = len(report)
    total_minutes = sum(r["minutes"] for r in report)
    total_goals = sum(r["goals"] for r in report)
    total_assists = sum(r["assists"] for r in report)

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # ---- TITLE ----
    elements.append(Paragraph(
        f"<b>Player Performance Report</b>", styles["Title"]
    ))

    elements.append(Paragraph(
        f"""
        <b>Name:</b> {player.name}<br/>
        <b>Position:</b> {player.position}<br/>
        <b>Team:</b> {player.team.name}<br/>
        <b>Filter:</b> {filter_type.capitalize()}
        """,
        styles["Normal"]
    ))

    elements.append(Paragraph("<br/>", styles["Normal"]))

    # ---- SUMMARY TABLE ----
    summary_table = Table([
        ["Appearances", "Minutes", "Goals", "Assists"],
        [appearances, total_minutes, total_goals, total_assists]
    ])

    summary_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))

    elements.append(summary_table)
    elements.append(Paragraph("<br/>", styles["Normal"]))

    # ---- MATCH TABLE ----
    match_table_data = [
        ["Date", "Minutes Played", "Goals", "Assists"]
    ]

    for r in report:
        match_table_data.append([
            r["date"],
            r["minutes"],
            r["goals"],
            r["assists"],
        ])

    match_table = Table(match_table_data, repeatRows=1)
    match_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
    ]))

    elements.append(match_table)

    doc.build(elements)

    response = HttpResponse(
        buffer.getvalue(),
        content_type="application/pdf"
    )
    response["Content-Disposition"] = (
        f'attachment; filename="{player.name}_player_report.pdf"'
    )
    return response
