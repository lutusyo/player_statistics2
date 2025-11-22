from django.shortcuts import render, get_object_or_404
from matches_app.models import Match
from teams_app.models import Team

def match_report_dashboard(request, match_id, our_team_id):
    """
    Match Report dashboard for a specific match and our team only.
    """

    match = get_object_or_404(Match, id=match_id)
    team = get_object_or_404(Team, id=our_team_id)

    context = {
        "match": match,
        "team": team,
    }

    return render(request, "reports_app/match_report_templates/match_report_dashboard.html", context)
