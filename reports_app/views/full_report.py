from django.shortcuts import render, get_object_or_404
from matches_app.models import Match
from tagging_app.utils.attempt_to_goal_utils import get_match_full_context
from gps_app.utils.gps_match_detail import get_gps_context
from reports_app.utils.stats import get_match_stats
from tagging_app.utils.pass_network_utils import get_pass_network_context
from matches_app.utils.match_details_utils import get_match_detail_context


def full_report_view(request, match_id, our_team_id):
    match = get_object_or_404(Match, id=match_id)

    # ======================
    # SCORE CALCULATION
    # ======================
    full_context = get_match_full_context(match.id, our_team_id)

    our_goals = full_context["our_team"]["aggregate"]["attempts"]["total_goals"]
    opponent_goals = full_context["opponent_team"]["aggregate"]["attempts"]["total_goals"]

    if match.home_team.id == our_team_id:
        home_score, away_score = our_goals, opponent_goals
    else:
        home_score, away_score = opponent_goals, our_goals

    result = f"{home_score} - {away_score}"

    # ======================
    # OTHER CONTEXT
    per_player_attempts = full_context['our_team']['per_player']['attempts']

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
        'match_number': getattr(match, 'match_number', None),
        'title': 'Full Match Report',
        'company': 'Azam Fc Analyst',

        # Teams
        'our_team': full_context['our_team'],
        'opponent_team': full_context['opponent_team'],

        # For template filters
        'outcomes_matrix': per_player_attempts,
        'players': full_context['our_team']['per_player'].keys(),
    }

    # Add other contexts
    context.update(get_match_stats(match))
    context.update(get_gps_context(match))
    context.update(get_pass_network_context(match_id))
    context.update(get_match_detail_context(match))

    return render(request, 'reports_app/full_report.html', context)
