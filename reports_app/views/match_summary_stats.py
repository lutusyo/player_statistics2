from django.shortcuts import render, get_object_or_404
from matches_app.models import Match
from reports_app.utils.stats import get_match_stats
from tagging_app.utils.attempt_to_goal_utils import get_attempt_to_goal_context

def match_summary_stats_view(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    home_score, away_score, result = get_attempt_to_goal_context(match)

    stats_context = get_match_stats(match)

    context = {
        'match': match,
        #'title': REPORT_TITLES['post-match-summary'],
        'company': 'Azam Fc Analyst',
        'competition': match.competition_type,
        'venue': match.venue,
        'date': match.date,
        'kickoff_time': match.time,
        'season': match.season,
        'match_number': getattr(match, 'match_number', None),
        'home_score': home_score,
        'away_score': away_score,
        'result': result,
        **stats_context,  # includes: our_team, opponent_team, possession, stats, etc.
    }

    return render(request, 'reports_app/intro_pages/match_summary_stats.html', context)
