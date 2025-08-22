# matches_app/views.py

from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from datetime import date
from collections import Counter, defaultdict

from players_app.models import PlayerCareerStage, Player
from teams_app.models import Team, AgeGroup
from lineup_app.models import MatchLineup, POSITION_COORDS
from lineup_app.views.match_lineup_view_with_uwanja import POSITION_COORDS
from matches_app.models import Match
from tagging_app.models import AttemptToGoal, GoalkeeperDistributionEvent

from tagging_app.views.pass_network import get_pass_network_data



@login_required
def match_detail(request, match_id):
    match = get_object_or_404(Match, pk=match_id)

    # Get all goals
    goals_qs = AttemptToGoal.objects.filter(
        match=match, outcome='On Target Goal'
    ).select_related('player', 'team', 'assist_by')

    home_player_ids = MatchLineup.objects.filter(
        match=match, team=match.home_team
    ).values_list('player_id', flat=True)

    away_player_ids = MatchLineup.objects.filter(
        match=match, team=match.away_team
    ).values_list('player_id', flat=True)

    home_goals, away_goals, goals = 0, 0, []
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

    # Lineup with coordinates
    def prepare_lineup(team, mirror=False):
        players = MatchLineup.objects.filter(match=match, team=team, is_starting=True).select_related("player")
        lineup = []
        for ml in players:
            coords = POSITION_COORDS.get(ml.position, {"top": 50, "left": 50})
            top = coords["top"]
            if mirror:
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

    # All attempts
    attempts = AttemptToGoal.objects.filter(match=match).select_related('player', 'team', 'assist_by')

    # Get pass stats per player (✅ moved outside the loop)
    players, player_names, matrix, total_passes, ball_lost = get_pass_network_data(match.id)

    # Prepare player statistics
    all_players = MatchLineup.objects.filter(match=match).select_related("player", "team")
    player_stats = []

    for ml in all_players:
        player = ml.player
        pid = player.id

        shots = AttemptToGoal.objects.filter(match=match, player=player)
        goals_count = shots.filter(outcome='On Target Goal').count()
        shots_on = shots.filter(outcome__in=['On Target Goal', 'On Target Miss']).count()
        assists = AttemptToGoal.objects.filter(match=match, assist_by=player).count()

        yellow_card = getattr(ml, 'yellow_card', 0)
        red_card = getattr(ml, 'red_card', 0)

        total = total_passes.get(pid, 0)
        lost = ball_lost.get(pid, 0)
        successful = total - lost
        accuracy = round((successful / total) * 100, 1) if total else 0

        player_stats.append({
            'player': player,
            'team': ml.team,
            'minutes_played': getattr(ml, 'minutes_played', 0),
            'shots': shots.count(),
            'shots_on': shots_on,
            'goals': goals_count,
            'assists': assists,
            'is_starting': ml.is_starting,
            'yellow_card': yellow_card,
            'red_card': red_card,
            'total_passes': total,
            'ball_lost': lost,
            'pass_accuracy': accuracy,
        })

    # --- Team level stats ---
    def calculate_team_passing(team_player_ids):
        return {
            'total_passes': sum(total_passes.get(pid, 0) for pid in team_player_ids),
            'ball_lost': sum(ball_lost.get(pid, 0) for pid in team_player_ids),
        }

    home_pass_stats = calculate_team_passing(home_player_ids)
    away_pass_stats = calculate_team_passing(away_player_ids)

    return render(request, 'matches_app/match_details.html', {
        'match': match,
        'lineup': lineup,
        'home_lineup': home_lineup,
        'away_lineup': away_lineup,
        'home_team_goals': home_goals,
        'away_team_goals': away_goals,
        'player_stats': player_stats,
        'attempts': attempts,
        'goals': goals,
        'home_pass_stats': home_pass_stats,
        'away_pass_stats': away_pass_stats,
    })
