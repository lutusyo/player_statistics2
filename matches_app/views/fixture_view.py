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
def fixtures_view(request, team):
    age_group = AgeGroup.objects.get(code=team)
    our_teams = Team.objects.filter(age_group=age_group, team_type='OUR_TEAM')

    upcoming_matches = Match.objects.filter(
        Q(home_team__in=our_teams) | Q(away_team__in=our_teams),
        date__gte=date.today()
    ).order_by('date')

    for match in upcoming_matches:
        # Set official match goals (if known)
        match.home_goals, match.away_goals = get_match_goals(match)

        # Check for lineup submitted by our team
        match.has_lineup = MatchLineup.objects.filter(match=match, team__in=our_teams).exists()

        # Use updated utility function
        context_data = get_attempt_to_goal_context(match.id)

        match.opponent_goals = context_data['opponent_goals'].count()
        match.our_team_goals = context_data['our_team_attempts'].filter(outcome='On Target Goal').count()

    context = {
        'team': team,
        'team_selected': team,
        'upcoming_matches': upcoming_matches,
        'active_tab': 'fixtures',
    }
    return render(request, 'matches_app/fixtures.html', context)
