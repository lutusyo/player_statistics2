from django.shortcuts import render, get_object_or_404
from teams_app.models import Team

def team_reports_view(request, team_id):
    """Team Reports Dashboard (technical reports navigation)."""
    team = get_object_or_404(Team, id=team_id)

    context = {
        'team': team,
    }
    return render(request, 'reports_app/team_reports/team_reports.html', context)
