from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from version1.matches_app.models import Match
from version1.matches_app.utils.match_details_utils import get_match_detail_context
from version1.tagging_app.utils.pass_network_utils import get_pass_network_context
from version1.tagging_app.utils.attempt_to_goal_utils import get_match_full_context # import new utility
from version1.tagging_app.models import AttemptToGoal

from version1.lineup_app.models import MatchLineup
from version1.gps_app.models import GPSRecord
from version1.teams_app.models import Team
 

@login_required
def match_detail(request, match_id):

    match = get_object_or_404(Match, id=match_id)

    our_team_id = match.home_team.id

    team = get_object_or_404(Team, id=our_team_id)

    # ⭐ SAME LOGIC AS RESULTS VIEW
    match.home_lineup_exists = MatchLineup.objects.filter(
        match=match,
        team=match.home_team
    ).exists()

    match.away_lineup_exists = MatchLineup.objects.filter(
        match=match,
        team=match.away_team).exists()

    match.has_gps_data = GPSRecord.objects.filter(
        match=match).exists()


    context = {
        'match': match,
        'our_team_id': our_team_id,
        'team': team,
    }

    details_context = get_match_detail_context(match)
    pass_network_context = get_pass_network_context(match, our_team_id)
    attempt_to_goal_context = get_match_full_context(match_id, our_team_id)

    context.update(details_context)
    context.update(pass_network_context)
    context.update(attempt_to_goal_context)

    return render(request, 'matches_app/match_details.html', context)