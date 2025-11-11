from django.shortcuts import render, get_object_or_404
from matches_app.models import Match

# Optional: Define report titles dictionary if used
REPORT_TITLES = {
    'setplays': 'Set Plays Report',
    # Add other report titles here if needed
}

def setplays_dashboard_intro(request, match_id, return_context=False):
    """
    View for displaying the fullscreen Set Plays intro page.
    """
    match = get_object_or_404(Match, id=match_id)

    context = {
        'match': match,
        'title': REPORT_TITLES.get('setplays', 'Set Plays'),
        'home_team': match.home_team,
        'away_team': match.away_team,
        'company': 'Azam FC Analyst',  # Company name for logo header
    }

    if return_context:
        return context

    return render(
        request,
        'reports_app/match_report_templates/7_set_plays/setplays_intro.html',
        context
    )
