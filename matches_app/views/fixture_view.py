from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Q
from datetime import date

from teams_app.models import Team, AgeGroup
from lineup_app.models import MatchLineup
from matches_app.models import Match
from matches_app.views.get_match_goals import get_match_goals
from tagging_app.utils.attempt_to_goal_utils import get_match_full_context


@login_required
def fixtures_view(request, team):
    # Get the age group for the team (e.g., U20)
    age_group = AgeGroup.objects.get(code=team)
    our_teams = Team.objects.filter(age_group=age_group)

    # Get all upcoming matches for our teams
    upcoming_matches = Match.objects.filter(
        Q(home_team__in=our_teams) | Q(away_team__in=our_teams),
        date__gte=date.today()
    ).order_by('date')

    # Loop through matches and add extra info
    for match in upcoming_matches:
        # Official goals (if available)
        match.home_goals, match.away_goals = get_match_goals(match)

        # Check if lineup exists for any of our teams
        match.has_lineup = MatchLineup.objects.filter(match=match, team__in=our_teams).exists()

        # Determine which team is ours
        our_team = match.home_team if match.home_team in our_teams else match.away_team
        match.our_team_id = our_team.id if our_team else None

        # Get full context (goal stats etc.)
        context_data = get_match_full_context(match.id, our_team.id)

        # Assign goal values
        match.our_team_goals = context_data["our_team"]["aggregate"]["attempts"]["total_goals"]
        match.opponent_goals = context_data["opponent_team"]["aggregate"]["attempts"]["total_goals"]

    # Prepare context for template
    context = {
        'team': team,
        'team_selected': team,
        'upcoming_matches': upcoming_matches,
        'active_tab': 'fixtures',
    }
    return render(request, 'matches_app/fixtures.html', context)
