# matches_app/views.py
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from version1.players_app.models import PlayerCareerStage, Player
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from reportlab.lib.pagesizes import A4
from datetime import date
from django.db.models import Q

from version1.teams_app.models import Team, AgeGroup
from version1.lineup_app.models import MatchLineup
from version1.matches_app.models import Match
from version1.tagging_app.models import AttemptToGoal, GoalkeeperDistributionEvent
from collections import Counter

from collections import defaultdict
from version1.matches_app.views.get_match_goals import get_match_goals

@login_required
def team_dashboard_view(request, team_id):

    team = Team.objects.get(id=team_id)

    # Just redirect to the fixtures view
    return redirect('matches_app:team_fixtures', team=team.age_group.code)