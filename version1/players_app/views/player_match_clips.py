from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import Http404
from collections import defaultdict

from version1.matches_app.models import Match
from version1.players_app.models import Player
from version1.defensive_app.models import PlayerDefensiveStats
from version1.tagging_app.models import AttemptToGoal, PassEvent, GoalkeeperDistributionEvent
from version1.lineup_app.models import MatchLineup, Substitution
from version1.teams_app.models import Team
from version1.reports_app.models import Result


def player_match_clips(request, player_id, match_id):
    player = get_object_or_404(Player, id=player_id)
    match = get_object_or_404(Match, id=match_id)

    attempts = AttemptToGoal.objects.filter(match=match, player=player).order_by('minute', 'second')

    goals = attempts.filter(outcome='ON TARGET GOAL')

    context = {
        'player': player,
        'match': match,
        'attempts': attempts,
        'goals': goals,
    }

    return render(request, 'players_app/player_match_clips.html', context)