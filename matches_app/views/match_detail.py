from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from matches_app.models import Match
from matches_app.utils.match_details_utils import get_match_detail_context
from tagging_app.utils.pass_network_utils import get_pass_network_context
from tagging_app.utils.attempt_to_goal_utils import get_match_full_context # import new utility
from tagging_app.models import AttemptToGoal


@login_required
def match_detail(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    our_team_id = match.home_team.id

    # Base context
    context = {
        'match': match,
        'our_team_id': our_team_id,
    }

    # Get match details context (lineups, h2h, goals, etc.)
    details_context = get_match_detail_context(match)

    # Get pass network context
    pass_network_context = get_pass_network_context(match)

    # Get attempt to goal context (with is_opponent handling)
    attempt_to_goal_context = get_match_full_context(match_id, our_team_id)

    # Tagged goals (On Target Goals) from both teams
    # You can optionally skip this if 'goals' already included in attempt_to_goal_context
    # But let's keep for compatibility
    goals = AttemptToGoal.objects.filter(
        match=match,
        outcome='On Target Goal'
    ).select_related('player', 'assist_by', 'team')

    # Merge all contexts into one
    context.update(details_context)
    context.update(pass_network_context)
    context.update(attempt_to_goal_context)
    #context['goals'] = goals  # or you can remove if you want to rely on attempt_to_goal_context

    return render(request, 'matches_app/match_details.html', context)
