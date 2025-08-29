from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Q
from datetime import date

from teams_app.models import Team, AgeGroup
from lineup_app.models import MatchLineup
from matches_app.models import Match
from matches_app.views.get_match_goals import get_match_goals
from tagging_app.utils.attempt_to_goal_utils import get_attempt_to_goal_context


@login_required
def results_view(request, team):
    age_group = AgeGroup.objects.get(code=team)
    our_teams = Team.objects.filter(age_group=age_group, team_type='OUR_TEAM')

    past_matches = Match.objects.filter(
        Q(home_team__in=our_teams) | Q(away_team__in=our_teams),
        date__lt=date.today()
    ).order_by('-date')

    for match in past_matches:
        # Goals from official match result
        match.home_goals, match.away_goals = get_match_goals(match)

        # Check if lineup exists
        match.has_lineup = MatchLineup.objects.filter(match=match).exists()

        # Use updated utility to get attempts context (our team and opponent attempts)
        context_data = get_attempt_to_goal_context(match.id)
        
        # opponent goals count
        match.opponent_goals = context_data['opponent_goals'].count()
        
        # our team goals count - from attempts with outcome "On Target Goal"
        match.our_team_goals = context_data['our_team_attempts'].filter(outcome='On Target Goal').count()

    context = {
        "team": team,
        'team_selected': team,
        'past_matches': past_matches,
        'active_tab': 'results',
    }
    return render(request, 'matches_app/match_results.html', context)
