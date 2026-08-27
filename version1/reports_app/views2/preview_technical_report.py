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

def preview_technical_report(request, team_id):
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
        end_date=end
    )

    context = {
        "team": team,
        "results": results,
        "stats": stats,
        "start": start,
        "end": end,
        "season": season,
    }

    return render(request, "reports_app/preview_technical_report.html",context)