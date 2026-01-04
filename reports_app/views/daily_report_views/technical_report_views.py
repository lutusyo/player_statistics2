import openpyxl
from openpyxl.styles import Font
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils.dateparse import parse_date

from teams_app.models import Team
from reports_app.models import Result, Medical, Transition, Scouting, Performance, IndividualActionPlan
from reports_app.views.daily_report_views.statistics_view import get_statistics_report


def write_sheet(ws, headers, rows):
    ws.append(headers)
    for cell in ws[1]:
        cell.font = Font(bold=True)
    for row in rows:
        ws.append(row)


def download_technical_report(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    season = request.GET.get("season", "")

    # Safe date parsing
    start_date_str = request.GET.get("start_date")
    end_date_str = request.GET.get("end_date")
    start_date = parse_date(start_date_str) if start_date_str else None
    end_date = parse_date(end_date_str) if end_date_str else None

    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    # Helper function to filter by date and season if applicable
    def filter_by_date(queryset, date_field='date'):
        if start_date:
            queryset = queryset.filter(**{f"{date_field}__gte": start_date})
        if end_date:
            queryset = queryset.filter(**{f"{date_field}__lte": end_date})
        if season and hasattr(queryset.model, 'season'):
            queryset = queryset.filter(season=season)
        return queryset

    # ================ RESULTS ================
    ws = wb.create_sheet("Results")
    results = filter_by_date(Result.objects.filter(our_team=team))
    write_sheet(
        ws,
        ["Date", "Competition", "Home", "Score", "Away", "Result"],
        [[r.date, r.competition_type, r.home_team.name, f"{r.home_score}-{r.away_score}", r.away_team.name, r.result] for r in results]
    )

    # ================ MEDICAL ================
    ws = wb.create_sheet("Medical")
    medicals = filter_by_date(Medical.objects.filter(squad=team))
    write_sheet(
        ws,
        ["Player", "Date", "Injury / Illness", "Status", "Comments"],
        [[m.name.name, m.date, m.injury_or_illness, m.status, m.comments] for m in medicals]
    )

    # ================ TRANSITION ================
    ws = wb.create_sheet("Transition")
    transitions = filter_by_date(Transition.objects.filter(squad=team))
    write_sheet(
        ws,
        ["Player", "Activity", "Played For", "Comments", "Date"],
        [[t.name.name, t.activity, t.played_for, t.comments, t.date] for t in transitions]
    )

    # ================ SCOUTING ================
    ws = wb.create_sheet("Scouting")
    scouting = filter_by_date(Scouting.objects.filter(squad=team))
    write_sheet(
        ws,
        ["Name", "DOB", "Position", "Agreement", "Former Club", "Comments"],
        [[s.name, s.dob, s.pos, s.agreement, s.former_club, s.comments] for s in scouting]
    )

    # ================ PERFORMANCE ================
    ws = wb.create_sheet("Performance")
    performances = filter_by_date(Performance.objects.filter(squad=team))
    write_sheet(
        ws,
        ["Date", "Activity", "Comments"],
        [[p.date, p.activity, p.comments] for p in performances]
    )

    # ================ INDIVIDUAL ACTION PLAN ================
    ws = wb.create_sheet("Individual Action Plan")
    iaps = filter_by_date(IndividualActionPlan.objects.filter(squad=team))
    write_sheet(
        ws,
        ["Player", "Category", "Responsibility", "Action", "Status", "Follow Up"],
        [[i.name.name, i.category, i.responsibility, i.action, i.status, i.follow_up] for i in iaps]
    )

    # ================ STATISTICS ================
    ws = wb.create_sheet("Statistics")
    stats_report = get_statistics_report(
        filter_type=request.GET.get("filter", "all"),
        team=team,
        start_date=start_date,
        end_date=end_date
    )

    headers = ["NAME", "POS", "TRAINING MINS", "GAME MINS", "APPS", "STARTS", "SUB IN", "SUB OUT", "GOALS", "ASSISTS", "NOTE"]
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

    # ================ DOWNLOAD ================
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    filename = f"Technical_Report_{team.age_group.code}_{season or 'ALL'}.xlsx"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    wb.save(response)
    return response


# Optional template view for filter form
def technical_report_filter(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    return render(request, "reports_app/technical_report_filter.html", {"team": team})
