from django.shortcuts import render, get_object_or_404
from matches_app.models import Match
from tagging_app.utils.attempt_to_goal_utils import get_attempt_to_goal_context
from gps_app.utils.gps_match_detail import get_gps_context
from reports_app.utils.stats import get_match_stats
from reports_app.views.intro_page import get_match_result
from tagging_app.utils.pass_network_utils import get_pass_network_context
from matches_app.utils.match_details_utils import get_match_detail_context 


def full_report_view(request, match_id):
    match = get_object_or_404(Match, id=match_id)

    # 1. Basic scores
    home_score, away_score, result = get_match_result(match)

    # 2. Attempt context (identifies our/opponent teams dynamically)
    attempt_to_goal_context = get_attempt_to_goal_context(match_id)

    # 3. Build context
    context = {
        'match': match,
        'home_team': match.home_team,
        'away_team': match.away_team,
        'home_score': home_score,
        'away_score': away_score,
        'result': result,
        'competition': match.competition_type,
        'venue': match.venue,
        'date': match.date,
        'kickoff_time': match.time,
        'season': match.season,
        'match_number': match.match_number if hasattr(match, 'match_number') else None,
        'title': 'Full Match Report',
        'company': 'Azam Fc Analyst',

        # ✅ Explicitly pass dynamically identified teams
        'our_team': attempt_to_goal_context['our_team'],
        'opponent_team': attempt_to_goal_context['opponent_team'],
    }

    # 4. Stats & GPS & Passing Network
    context.update(get_match_stats(match))
    context.update(get_gps_context(match))
    context.update(get_pass_network_context(match_id))
    context.update(get_match_detail_context(match))
    context.update(attempt_to_goal_context)

    return render(request, 'reports_app/full_report.html', context)
