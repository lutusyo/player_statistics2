from django.shortcuts import render, get_object_or_404
from matches_app.models import Match
from teams_app.models import Team
from django.template.loader import render_to_string
from .intro_page import get_match_result, REPORT_TITLES  # reuse your logic
from django.shortcuts import render, get_object_or_404
from matches_app.models import Match

from reports_app.utils.stats import get_match_stats  # assuming your function is here


def render_intro_section(match, report_type):
    home_score, away_score, result = get_match_result(match)
    
    context = {
        'match': match,
        'home_team': match.home_team,
        'away_team': match.away_team,
        'title': REPORT_TITLES.get(report_type, report_type),
        'company': 'Azam Fc Analyst',
        'report_type': report_type,
        'home_score': home_score,
        'away_score': away_score,
        'result': result,
    }

    if report_type == 'post-match-summary':
        context.update({
            'competition': match.competition_type,
            'venue': match.venue,
            'date': match.date,
            'kickoff_time': match.time,
            'season': match.season,
        })

        # Add full match stats context
        match_stats = get_match_stats(match)
        context.update(match_stats)

    return render_to_string('reports_app/intro_page.html', context)





REPORT_TYPES = [
    'post-match-summary',
    'in-possession',
    'out-of-possession',
    'goalkeeping',
    'set-plays',
    'individual-in-possession',
    'individual-out-of-possession',
    'individual-physical',
]

def full_report_view(request, match_id):
    match = get_object_or_404(Match, id=match_id)

    # Render each intro section
    intro_sections = [render_intro_section(match, rt) for rt in REPORT_TYPES]

    return render(request, 'reports_app/full_report.html', {
        'intro_sections': intro_sections,
        'match': match,
    })

