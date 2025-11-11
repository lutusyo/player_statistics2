from django.shortcuts import render, get_object_or_404
from matches_app.models import Match

# Optional: Define report titles dictionary if used
REPORT_TITLES = {
    'goalkeeping': 'Goalkeeping Report',
    # Add other report titles here if needed
}

def goalkeeping_intro_view(request, match_id, return_context=False):
    """
    View for displaying the fullscreen Goalkeeping intro page.
    """
    match = get_object_or_404(Match, id=match_id)

    context = {
        'match': match,
        'title': REPORT_TITLES.get('goalkeeping', 'Goalkeeping'),
        'home_team': match.home_team,
        'away_team': match.away_team,
        'company': 'Azam FC Analyst',  # Company name for logo header
    }

    if return_context:
        return context

    return render(
        request,
        'reports_app/match_report_templates/6_goalkeeping/goalkeeping_intro.html',
        context
    )
