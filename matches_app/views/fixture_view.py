# matches_app/views.py
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from players_app.models import PlayerCareerStage, Player
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from reportlab.lib.pagesizes import A4
from datetime import date

from django.db.models import Q
from teams_app.models import Team, AgeGroup
from lineup_app.models import MatchLineup, POSITION_COORDS
from tagging_app.models import AttemptToGoal, GoalkeeperDistributionEvent
from collections import Counter
from matches_app.models import Match

from collections import defaultdict
from matches_app.views.get_match_goals import get_match_goals






@login_required
def fixtures_view(request, team):
    age_group = AgeGroup.objects.get(code=team)
    our_teams = Team.objects.filter(age_group=age_group, team_type='OUR_TEAM')

    upcoming_matches = Match.objects.filter(
        Q(home_team__in=our_teams) | Q(away_team__in=our_teams),
        date__gte=date.today()
    ).order_by('date')

    for match in upcoming_matches:
        # Add goals
        match.home_goals, match.away_goals = get_match_goals(match)

        # Check if lineup exists for this match
        match.has_lineup = MatchLineup.objects.filter(match=match, team__in=our_teams).exists()

    context = {
        'team': team,
        'upcoming_matches': upcoming_matches,
        'team_selected': team,
        'active_tab': 'fixtures',
    }
    return render(request, 'matches_app/fixtures.html', context)
