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
from lineup_app.models import MatchLineup
from matches_app.models import Match
from tagging_app.models import AttemptToGoal, GoalkeeperDistributionEvent
from collections import Counter

from collections import defaultdict
from lineup_app.views.match_lineup_view_with_uwanja import POSITION_COORDS



from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from lineup_app.models import MatchLineup, POSITION_COORDS
from lineup_app.views.match_lineup_view_with_uwanja import POSITION_COORDS
#from matches_app.models import Match
from tagging_app.models import AttemptToGoal

@login_required
def match_detail(request, match_id):
    match = get_object_or_404(Match, pk=match_id)

    # Goals
    goals_qs = AttemptToGoal.objects.filter(
        match=match, outcome='On Target Goal'
    ).select_related('player', 'team', 'assist_by')

    home_player_ids = MatchLineup.objects.filter(
        match=match, team=match.home_team
    ).values_list('player_id', flat=True)
    away_player_ids = MatchLineup.objects.filter(
        match=match, team=match.away_team
    ).values_list('player_id', flat=True)

    home_goals = 0
    away_goals = 0
    goals = []

    for goal in goals_qs:
        if goal.player_id in home_player_ids:
            home_goals += 1
            team_name = match.home_team.name
        elif goal.player_id in away_player_ids:
            away_goals += 1
            team_name = match.away_team.name
        else:
            if goal.team_id == match.home_team_id:
                home_goals += 1
                team_name = match.home_team.name
            elif goal.team_id == match.away_team_id:
                away_goals += 1
                team_name = match.away_team.name
            else:
                team_name = "Unknown"

        goals.append({
            'minute': goal.minute,
            'second': goal.second,
            'scorer': goal.player.name if goal.player else "Unknown",
            'assist_by': goal.assist_by.name if goal.assist_by else None,
            'is_own_goal': False,
            'team_name': team_name,
        })

    # -------- LINEUP WITH COORDINATES --------
    def prepare_lineup(team, mirror=False):
        players = MatchLineup.objects.filter(match=match, team=team, is_starting=True).select_related("player")
        lineup = []
        for ml in players:
            coords = POSITION_COORDS.get(ml.position, {"top": 50, "left": 50})
            top = coords["top"]
            if mirror:  # flip for away team
                top = 100 - top
            lineup.append({
                "id": ml.player.id,
                "name": ml.player.name,
                "number": getattr(ml.player, "jersey_number", ""),
                "top": top,
                "left": coords["left"],
            })
        return lineup

    home_lineup = prepare_lineup(match.home_team)
    away_lineup = prepare_lineup(match.away_team, mirror=True)
    lineup = home_lineup + away_lineup

    return render(request, 'matches_app/match_details.html', {
        'match': match,
        'lineup': lineup,
        'home_team_name': match.home_team.name,
        'away_team_name': match.away_team.name,
        'home_team_goals': home_goals,
        'away_team_goals': away_goals,
        'goals': goals,
        'home_lineup': home_lineup,
        'away_lineup': away_lineup,
    })
