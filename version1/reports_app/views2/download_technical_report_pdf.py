import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils.dateparse import parse_date
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

from version1.teams_app.models import Team
from version1.reports_app.models.previous_models import Result, Medical, Transition, Scouting, Performance, IndividualActionPlan
from version1.reports_app.views.daily_report_views.statistics_view import get_statistics_report
from version1.players_app.models import Player

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import ( SimpleDocTemplate, Paragraph,Spacer,Table,TableStyle,PageBreak,)

from reportlab.lib.pagesizes import A4, landscape
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN


def get_full_name(player):
    """Return the full player name as: First + Second + Surname"""
    if not player:
        return ""
    return f"{player.name} {player.second_name} {player.surname}".strip()

def download_technical_report_pdf(request, team_id):
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
        team=team, start_date=start, end_date=end
    )

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="Technical_Report_'
        f'{team.age_group.code}_{season or "ALL"}.pdf"'
    )

    doc = SimpleDocTemplate(
        response, pagesize=landscape(A4),
        rightMargin=6*mm, leftMargin=6*mm,
        topMargin=10*mm, bottomMargin=10*mm
    )
    styles = getSampleStyleSheet()
    story = [
        Paragraph(f"MATCH RESULTS - {team.name}", styles["Title"]),
        Paragraph(f"Period: {start or 'All'} to {end or 'All'}", styles["Normal"]),
        Spacer(1, 8)
    ]

    # PAGE 1 - RESULTS
    data = [["DATE", "COMPETITION", "HOME", "SCORE", "AWAY", "RESULT", "GOAL SCORERS"]]

    for r in results:
        scorers = []
        for s in (r.goal_scorers or "").split(","):
            s = s.strip()
            if s:
                try:
                    name, minute = s.rsplit(" ", 1)
                    p = Player.objects.filter(name__iexact=name).first()
                    scorers.append(f"{get_full_name(p)} {minute}" if p else s)
                except ValueError:
                    scorers.append(s)

        data.append([
            r.date, r.competition_type, r.home_team.name,
            f"{r.home_score}-{r.away_score}", r.away_team.name,
            r.result, ", ".join(scorers)
        ])

    table = Table(data, colWidths=[22*mm,35*mm,40*mm,20*mm,40*mm,25*mm,70*mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#0070C0")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 8),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("GRID", (0,0), (-1,-1), .5, colors.grey),
    ]))
    story.append(table)

    # PAGE 2 - STATISTICS
    story.append(PageBreak())
    story.append(Paragraph(f"TECHNICAL REPORT - {team.name}", styles["Title"]))

    data = [
        ["PLAYER", "POS", "MATCH DATA", "", "", "", "", "", "", "", "",
         "TRAINING DATA", "", "", "", "", "", "", ""],
        ["Player", "Pos", "Game Mins", "Apps", "Starts", "Sub In", "Sub Out",
         "Goals", "Assists", "Pre-Assists", "Note", "Training Total",
         "U11", "U13", "U15", "U17", "U20", "First Team", "National Team"]
    ]

    for r in stats:
        p = r["player"]
        data.append([
            get_full_name(p), r.get("position", ""),
            r.get("game_minutes", 0), r.get("appearances", 0),
            r.get("starts", 0), r.get("sub_in", 0), r.get("sub_out", 0),
            r.get("goals", 0), r.get("assists", 0), r.get("pre_assists", 0),
            r.get("note", ""), r.get("training_total", 0),
            r.get("training_u11", 0), r.get("training_u13", 0),
            r.get("training_u15", 0), r.get("training_u17", 0),
            r.get("training_u20", 0), r.get("training_first", 0),
            r.get("training_national", 0)
        ])

    table = Table(data, colWidths=[
        28*mm,15*mm,17*mm,12*mm,13*mm,13*mm,14*mm,
        12*mm,16*mm,18*mm,27*mm,19*mm,12*mm,12*mm,
        12*mm,12*mm,12*mm,17*mm,19*mm
    ], repeatRows=2)

    table.setStyle(TableStyle([
        ("SPAN",(0,0),(0,1)), ("SPAN",(1,0),(1,1)),
        ("SPAN",(2,0),(10,0)), ("SPAN",(11,0),(18,0)),
        ("BACKGROUND",(0,0),(1,1),colors.HexColor("#0070C0")),
        ("BACKGROUND",(2,0),(10,1),colors.HexColor("#1F4E78")),
        ("BACKGROUND",(11,0),(18,1),colors.HexColor("#548235")),
        ("TEXTCOLOR",(0,0),(-1,1),colors.white),
        ("FONTNAME",(0,0),(-1,1),"Helvetica-Bold"),
        ("FONTSIZE",(0,0),(-1,-1),6.5),
        ("ALIGN",(0,0),(-1,-1),"CENTER"),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("GRID",(0,0),(-1,-1),.4,colors.grey),
    ]))

    story.append(table)
    doc.build(story)
    return response