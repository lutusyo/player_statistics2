from django.shortcuts import render, get_object_or_404
from matches_app.models import Match
from tagging_app.models import AttemptToGoal
from gps_app.utils.gps_match_detail import get_gps_context
from reports_app.utils.stats import get_match_stats
from reports_app.views.intro_page import get_match_result
from tagging_app.utils.pass_network_utils import get_pass_network_context
from tagging_app.utils.attempt_to_goal_utils import get_attempt_to_goal_context
from matches_app.utils.match_details_utils import get_match_detail_context 



def full_report_view(request, match_id):
    match = get_object_or_404(Match, id=match_id)

    # 1. Get scores using your helper
    home_score, away_score, result = get_match_result(match)


    # 4. Final unified context
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
        # Add your other report data here:
        #'in_possession_data': get_in_possession_data(match),
        #'out_of_possession_data': get_out_of_possession_data(match),
        # ...
    }


    # 2. Match stats for match_summary.html
    match_stats_context = get_match_stats(match)  # Must return a dictionary
    # 5. Merge in match stats and GPS context
    context.update(match_stats_context)

    # 3. GPS data for individual_physical.html
    gps_context = get_gps_context(match)
    context.update(gps_context)

    pass_network_context = get_pass_network_context(match_id)
    context.update(pass_network_context)

    

    attempt_to_goal_context = get_attempt_to_goal_context(match_id)
    context.update(attempt_to_goal_context)

    match_detail_context =  get_match_detail_context(match)
    context.update(match_detail_context)
    

    # 6. Render full report with all sections
    return render(request, 'reports_app/full_report.html', context)
