from django.shortcuts import render, get_object_or_404
from django.db.models import Sum, Q
from django.utils.timezone import now
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from io import BytesIO
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from django.utils.dateparse import parse_date

from version1.players_app.models import Player
from version1.lineup_app.models import MatchLineup
from version1.tagging_app.models import AttemptToGoal
from version1.teams_app.models import Team
from version1.reports_app.models.previous_models import PlayerTrainingMinutes
from version1.matches_app.models import CompetitionType
from version1.reports_app.models.previous_models import (PlayerTrainingMinutes,TrainingMinutes,)
from version1.reports_app.models.weekly_report import WeeklyReport

from reportlab.lib.pagesizes import A4, landscape


# ====================== REPORT HELPER ======================
def get_statistics_report(filter_type="all", team=None, start_date=None, end_date=None, competition=None):
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

    # Match competition filter
    if competition:
        match_filter &= Q(match__competition__type=competition)

    report = []

    players = Player.objects.filter(is_active=True,status="SIGNED", team=team)

    for player in players:
        lineups = MatchLineup.objects.filter(player=player).filter(match_filter)

        appearances = lineups.count()
        starts = lineups.filter(is_starting=True).count()
        sub_in = lineups.filter(is_starting=False, time_in__isnull=False).count()
        sub_out = lineups.filter(time_out__isnull=False).count()
        game_minutes = lineups.aggregate(total=Sum('minutes_played'))['total'] or 0

        # Goals
        goals = AttemptToGoal.objects.filter(
            player=player, outcome='On Target Goal'
        ).filter(match_filter).count()

        # Assists (player assisted a goal)
        assists = AttemptToGoal.objects.filter(
            assist_by=player, outcome='On Target Goal'
        ).filter(match_filter).count()

        # Pre-assists (player made the pass before the assist)
        pre_assists = AttemptToGoal.objects.filter(
            pre_assist_by=player,  # assuming you have a field pre_assist_by
            outcome='On Target Goal'
        ).filter(match_filter).count()

        # Getting all Training records for the player
        training_minutes_qs = PlayerTrainingMinutes.objects.filter(player=player)

        if start_date:
            training_minutes_qs = training_minutes_qs.filter(training_session__date__gte=start_date)

        if end_date:
            training_minutes_qs = training_minutes_qs.filter(training_session__date__lte=end_date)

        # Total minutes
        training_total = training_minutes_qs.aggregate(
            total=Sum("minutes"))["total"] or 0

        # Minutes with each team
        u11_minutes = training_minutes_qs.filter(
            trained_with_team__team_category="CLUB",
            trained_with_team__age_group__code="U11"
        ).aggregate(total=Sum("minutes"))["total"] or 0

        # Minutes with each team
        u13_minutes = training_minutes_qs.filter(
            trained_with_team__team_category="CLUB",
            trained_with_team__age_group__code="U13"
        ).aggregate(total=Sum("minutes"))["total"] or 0

        # Minutes with each team
        u15_minutes = training_minutes_qs.filter(
            trained_with_team__team_category="CLUB",
            trained_with_team__age_group__code="U15"
        ).aggregate(total=Sum("minutes"))["total"] or 0        

        # Minutes with each team
        u17_minutes = training_minutes_qs.filter(
            trained_with_team__team_category="CLUB",
            trained_with_team__age_group__code="U17"
        ).aggregate(total=Sum("minutes"))["total"] or 0

        u20_minutes = training_minutes_qs.filter(
            trained_with_team__team_category="CLUB",
            trained_with_team__age_group__code="U20"
        ).aggregate(total=Sum("minutes"))["total"] or 0

        first_team_minutes = training_minutes_qs.filter(
            trained_with_team__team_category="CLUB",
            trained_with_team__age_group__code="Senior"
        ).aggregate(total=Sum("minutes"))["total"] or 0

        national_team_minutes = training_minutes_qs.filter(
            trained_with_team__team_category="NATIONAL"
        ).aggregate(total=Sum("minutes"))["total"] or 0

        report.append({
            "player": player,
            "position": player.position,

            "training_total": training_total,
            "training_u11": u11_minutes,
            "training_u13": u13_minutes,
            "training_u15": u15_minutes,
            "training_u17": u17_minutes,
            "training_u20": u20_minutes,
            "training_first": first_team_minutes,
            "training_national": national_team_minutes,

            "game_minutes": game_minutes,
            "appearances": appearances,
            "starts": starts,
            "sub_in": sub_in,
            "sub_out": sub_out,
            "goals": goals,
            "assists": assists,
            "pre_assists": pre_assists,
            "note": "",
        })

    return report



def get_statistics_context(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    filter_type = request.GET.get("filter", "all")
    competition = request.GET.get("competition") or None

    start_date = parse_date(request.GET.get("start_date", ""))
    end_date = parse_date(request.GET.get("end_date", ""))

    if not start_date:
        today = now().date()

        if filter_type == "week":
            start_date = today - timedelta(days=7)
        elif filter_type == "month":
            start_date = today.replace(day=1)

    report = get_statistics_report(
        filter_type=filter_type,
        team=team,
        start_date=start_date,
        end_date=end_date,
        competition=competition,
    )

    return {
        "report": report,
        "team": team,
        "filter_type": filter_type,
        "start_date": start_date,
        "end_date": end_date,
        "competition": competition,
        "competition_choices": CompetitionType.choices,
    }


@login_required
def statistics_list_view(request, team_id):
    context = get_statistics_context(request, team_id)

    return render(request, "reports_app/daily_report_templates/9statistics/statistics_list.html", context,)




STAT_COLUMNS = [
    ("Name", lambda r: r["player"].full_name),
    ("Pos", lambda r: r["position"]),
    ("Total min", lambda r: r["game_minutes"]),
    ("Games", lambda r: r["appearances"]),
    ("Starts", lambda r: r["starts"]),
    ("In", lambda r: r["sub_in"]),
    ("Out", lambda r: r["sub_out"]),
    ("Goals", lambda r: r["goals"]),
    ("Ast", lambda r: r["assists"]),
    ("Pre Ast", lambda r: r["pre_assists"]),
    ("Training Total", lambda r: r["training_total"]),
    ("U11", lambda r: r["training_u11"]),
    ("U13", lambda r: r["training_u13"]),
    ("U15", lambda r: r["training_u15"]),
    ("U17", lambda r: r["training_u17"]),
    ("U20", lambda r: r["training_u20"]),
    ("First", lambda r: r["training_first"]),
    ("National", lambda r: r["training_national"]),
]


def get_export_data(report):
    return [
        [get_value(r) for _, get_value in STAT_COLUMNS]
        for r in report
    ]



@login_required
def statistics_export_excel(request, team_id):
    context = get_statistics_context(request, team_id)

    df = pd.DataFrame(
        get_export_data(context["report"]),
        columns=[name for name, _ in STAT_COLUMNS],
    )

    output = BytesIO()
    df.to_excel(output, index=False, engine="openpyxl")

    response = HttpResponse(
        output.getvalue(),
        content_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
    )
    response["Content-Disposition"] = (
        f'attachment; filename="Player_Stats_'
        f'{context["team"].age_group.code}.xlsx"'
    )
    return response



@login_required
def statistics_export_pdf(request, team_id):
    context = get_statistics_context(request, team_id)

    data = [
        [name for name, _ in STAT_COLUMNS],
        *get_export_data(context["report"]),
    ]

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
    )

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.gray),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 6),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.black),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))

    doc.build([
        Paragraph("Player Statistics Report",
                  getSampleStyleSheet()["Heading2"]),
        table,
    ])

    response = HttpResponse(
        buffer.getvalue(),
        content_type="application/pdf",
    )
    response["Content-Disposition"] = (
        'attachment; filename="player_stats.pdf"'
    )
    return response


