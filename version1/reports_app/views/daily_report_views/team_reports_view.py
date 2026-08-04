from django.shortcuts import render, get_object_or_404
from version1.reports_app.models.weekly_report import WeeklyReport

from version1.teams_app.models import Team

def team_reports_view(request, team_id):
    """Team Reports Dashboard (technical reports navigation)."""
    team = get_object_or_404(Team, id=team_id)
    report = WeeklyReport.objects.filter(team=team).order_by("-id").first()

    context = {
        'team': team,
        "report": report,
    }
    
    return render(request, 'reports_app/team_reports/team_reports.html', context)
