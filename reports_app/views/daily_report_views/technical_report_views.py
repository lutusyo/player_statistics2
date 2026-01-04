import openpyxl
from openpyxl.styles import Font
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from teams_app.models import Team
from matches_app.models import Match
from reports_app.models import (
    Result, Medical, Transition, Scouting,
    Performance, IndividualActionPlan, TrainingMinutes, PlayerTrainingMinutes
)
from tagging_app.models import (
    AttemptToGoal, PassEvent, GoalkeeperDistributionEvent
)

from reports_app.views.daily_report_views.statistics_view import get_statistics_report



def write_sheet(ws, headers, rows):
    ws.append(headers)
    for cell in ws[1]:
        cell.font = Font(bold=True)
    for row in rows:
        ws.append(row)


def download_technical_report(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    age_group = team.age_group
    season = request.GET.get("season")

    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    # ================= RESULTS =================
    ws = wb.create_sheet("Results")
    results = Result.objects.filter(our_team=team)
    if season:
        results = results.filter(season=season)

    write_sheet(
        ws,
        ["Date", "Competition", "Home", "Score", "Away", "Result"],
        [
            [
                r.date,
                r.competition_type,
                r.home_team.name,
                f"{r.home_score}-{r.away_score}",
                r.away_team.name,
                r.result,
            ]
            for r in results
        ],
    )

    # ================= MEDICAL =================
    ws = wb.create_sheet("Medical")
    medicals = Medical.objects.filter(squad=team)
    write_sheet(
        ws,
        ["Player", "Date", "Injury / Illness", "Status", "Comments"],
        [
            [m.name.name, m.date, m.injury_or_illness, m.status, m.comments]
            for m in medicals
        ],
    )

    # ================= TRANSITION =================
    ws = wb.create_sheet("Transition")
    transitions = Transition.objects.filter(squad=team)
    write_sheet(
        ws,
        ["Player", "Activity", "Played For", "Comments", "Date"],
        [
            [t.name.name, t.activity, t.played_for, t.comments, t.date]
            for t in transitions
        ],
    )

    # ================= SCOUTING =================
    ws = wb.create_sheet("Scouting")
    scouting = Scouting.objects.filter(squad=team)
    write_sheet(
        ws,
        ["Name", "DOB", "Position", "Agreement", "Former Club", "Comments"],
        [
            [s.name, s.dob, s.pos, s.agreement, s.former_club, s.comments]
            for s in scouting
        ],
    )

    # ================= PERFORMANCE =================
    ws = wb.create_sheet("Performance")
    performances = Performance.objects.filter(squad=team)
    write_sheet(
        ws,
        ["Date", "Activity", "Comments"],
        [[p.date, p.activity, p.comments] for p in performances],
    )

    # ================= IAP =================
    ws = wb.create_sheet("Individual Action Plan")
    iaps = IndividualActionPlan.objects.filter(squad=team)
    write_sheet(
        ws,
        ["Player", "Category", "Responsibility", "Action", "Status", "Follow Up"],
        [
            [
                i.name.name,
                i.category,
                i.responsibility,
                i.action,
                i.status,
                i.follow_up,
            ]
            for i in iaps
        ],
    )

    # ================= STATISTICS (PLAYER SUMMARY) =================
    ws = wb.create_sheet("Statistics")
    stats_report = get_statistics_report(
        filter_type=request.GET.get("filter", "all"),
        team=team
    )

    headers = [
        "NAME", "POS", "TRAINING MINS", "GAME MINS",
        "APPS", "STARTS", "SUB IN", "SUB OUT",
        "GOALS", "ASSISTS", "NOTE"
    ]
    ws.append(headers)
    for cell in ws[1]:
        cell.font = Font(bold=True)

    for r in stats_report:
        ws.append([
            r["player"].name,
            r["position"],
            r["training_minutes"],
            r["game_minutes"],
            r["appearances"],
            r["starts"],
            r["sub_in"],
            r["sub_out"],
            r["goals"],
            r["assists"],
            r["note"],
        ])

    # ================= DOWNLOAD =================
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    filename = f"Technical_Report_{team.age_group.code}_{season or 'ALL'}.xlsx"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    wb.save(response)
    return response
