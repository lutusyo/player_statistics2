import os
from django.utils.timezone import now
from django.utils.dateparse import parse_date
from datetime import timedelta
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
import json
from django.http import HttpResponse
from django.db.models import Q
from io import BytesIO
import pandas as pd
import matplotlib.pyplot as plt

# PDF imports
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from django.conf import settings

from version1.lineup_app.models import MatchLineup
from version1.tagging_app.models import AttemptToGoal
from version1.players_app.models import Player

# Helper functions
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

    lineups = MatchLineup.objects.filter(match_filter).select_related("match").order_by("match__date")
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

def generate_chart_image(data, labels, title):
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot(labels, data, marker='o', linestyle='-', color='blue')
    ax.set_title(title)
    ax.set_xlabel('Match #')
    ax.set_ylabel(title)
    ax.grid(True)
    buf = BytesIO()
    plt.tight_layout()
    fig.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    return buf


# Views
@login_required
def player_report_view(request, player_id):
    player = get_object_or_404(Player, id=player_id)
    filter_type = request.GET.get("filter", "all")
    start_date = parse_date(request.GET.get("start_date")) if request.GET.get("start_date") else None
    end_date = parse_date(request.GET.get("end_date")) if request.GET.get("end_date") else None

    # Filtered report
    report = get_individual_player_report(player, filter_type, start_date, end_date)
    summary = get_player_summary(player, report)

    context = {
        "player": player,
        "summary": summary,
        "report": report,
        "filter_type": filter_type,
        "start_date": start_date,
        "end_date": end_date,
        "labels_json": json.dumps([r["match_no"] for r in report]),
        "minutes_json": json.dumps([r["minutes"] for r in report]),
        "goals_json": json.dumps([r["goals"] for r in report]),
        "assists_json": json.dumps([r["assists"] for r in report]),
        "total_minutes_json": json.dumps([r["minutes"] for r in report]),
        "total_goals_json": json.dumps([r["goals"] for r in report]),
        "total_assists_json": json.dumps([r["assists"] for r in report]),
    }
    return render(request, "reports_app/daily_report_templates/9statistics/player_report.html", context)

@login_required
def player_report_export_excel(request, player_id):
    player = get_object_or_404(Player, id=player_id)
    filter_type = request.GET.get("filter", "all")
    start_date = parse_date(request.GET.get("start_date")) if request.GET.get("start_date") else None
    end_date = parse_date(request.GET.get("end_date")) if request.GET.get("end_date") else None

    report = get_individual_player_report(player, filter_type, start_date, end_date)
    df = pd.DataFrame(report)

    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Match Report")

    response = HttpResponse(output.getvalue(),
                            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = f'attachment; filename="{player.name}_report.xlsx"'
    return response

@login_required
def player_report_export_pdf(request, player_id):
    player = get_object_or_404(Player, id=player_id)
    filter_type = request.GET.get("filter", "all")
    start_date_str = request.GET.get("start_date")
    end_date_str = request.GET.get("end_date")
    start_date = parse_date(start_date_str) if start_date_str else None
    end_date = parse_date(end_date_str) if end_date_str else None

    # Use only filtered report
    report = get_individual_player_report(player, filter_type, start_date, end_date)
    summary = get_player_summary(player, report)

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    elements.append(Paragraph("<b>Player Performance Report</b>", styles["Title"]))
    elements.append(Spacer(1, 12))

    # Player photo
    try:
        img_path = None
        if player.photo and os.path.exists(player.photo.path):
            img_path = player.photo.path
        else:
            default_img = os.path.join(settings.BASE_DIR, "static", "images", "default_player.png")
            if os.path.exists(default_img):
                img_path = default_img
        if img_path:
            elements.append(Image(img_path, width=4*cm, height=4*cm))
        else:
            elements.append(Paragraph("Player photo not available", styles["Normal"]))
    except:
        elements.append(Paragraph("Player photo not available", styles["Normal"]))
    elements.append(Spacer(1, 12))

    # Player info
    info_text = f"""
        <b>Name:</b> {player.name}<br/>
        <b>Position:</b> {player.position}<br/>
        <b>Team:</b> {player.team.name}<br/>
        <b>Filter:</b> {filter_type.capitalize()}<br/>
    """
    if start_date:
        info_text += f"<b>From:</b> {start_date}<br/>"
    if end_date:
        info_text += f"<b>To:</b> {end_date}<br/>"
    elements.append(Paragraph(info_text, styles["Normal"]))
    elements.append(Spacer(1, 12))

    # Summary Table
    summary_table = Table([
        ["Appearances", "Minutes", "Goals", "Assists"],
        [summary["appearances"], summary["minutes"], summary["goals"], summary["assists"]]
    ])
    summary_table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, colors.black),
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 12))

    # Match-by-match table (filtered only)
    match_table_data = [["#", "Date", "Minutes", "Goals", "Assists"]]
    for r in report:
        match_table_data.append([r["match_no"], r["date"].strftime("%Y-%m-%d"), r["minutes"], r["goals"], r["assists"]])
    match_table = Table(match_table_data, repeatRows=1)
    match_table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, colors.black),
        ("BACKGROUND", (0,0), (-1,0), colors.whitesmoke),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
    ]))
    elements.append(match_table)
    elements.append(Spacer(1, 12))

    # Charts (filtered only)
    chart_titles = ["Minutes Played", "Goals", "Assists"]
    chart_data = [
        [r["minutes"] for r in report],
        [r["goals"] for r in report],
        [r["assists"] for r in report]
    ]
    for title, data in zip(chart_titles, chart_data):
        if data:
            buf = generate_chart_image(data, [r["match_no"] for r in report], title)
            img = Image(buf, width=16*cm, height=8*cm)
            elements.append(Paragraph(f"<b>{title} Chart</b>", styles["Normal"]))
            elements.append(img)
            elements.append(Spacer(1, 12))

    # Build PDF
    doc.build(elements)
    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{player.name}_player_report_filtered.pdf"'
    return response