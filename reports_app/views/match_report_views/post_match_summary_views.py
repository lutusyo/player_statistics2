from django.shortcuts import render, get_object_or_404
from matches_app.models import Match
from gps_app.utils.gps_match_detail import get_gps_context
from reports_app.utils.stats import get_match_stats
from matches_app.utils.match_details_utils import get_match_detail_context
from tagging_app.utils.pass_network_utils import get_pass_network_context
from tagging_app.utils.attempt_to_goal_utils import get_match_full_context
from tagging_app.utils.attempt_to_goal_utils_opp import get_opponent_goals_for_match


def full_match_context_view(request, match_id, return_context=False):
    """
    Full context for a match with home and away pass network included.
    """
    match = get_object_or_404(Match, id=match_id)

    # TEAM CONTEXT
    full_context = get_match_full_context(match_id, match.home_team.id)

    # MATCH DETAILS
    match_detail_context = get_match_detail_context(match)

    home_score = match_detail_context["home_team_goals"]
    away_score = match_detail_context["away_team_goals"]
    result = f"{home_score} - {away_score}"

    # OTHER CONTEXTS
    gps_context = get_gps_context(match)
    stats_context = get_match_stats(match)

    # PASS NETWORKS for home and away
    home_pass_context = get_pass_network_context(match, match.home_team.id)
    away_pass_context = get_pass_network_context(match, match.away_team.id)

    # FINAL CONTEXT
    context = {
        'match': match,
        'home_team': match.home_team,
        'away_team': match.away_team,
        'home_score': home_score,
        'away_score': away_score,
        'result': result,
        'title': 'Full Match Context',
        'company': 'Azam Fc Analyst',

        'competition': match.competition,
        'venue': match.venue,
        'date': match.date,
        'kickoff_time': match.time,
        'season': match.season,
        'match_number': getattr(match, 'match_number', None),

        # Extra contexts
        **gps_context,
        **stats_context,
        **match_detail_context,

        # Home & Away Pass Network
        'home_pass_context': home_pass_context,
        'away_pass_context': away_pass_context,
    }

    if return_context:
        return context

    return render(request,'reports_app/match_report_templates/1_post_match_summary/post_match_summary.html',context)
