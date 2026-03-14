from lineup_app.models import MatchLineup, POSITION_COORDS
from tagging_app.models import AttemptToGoal
from tagging_app.utils.pass_network_utils import get_pass_network_context
from gps_app.models import GPSRecord


def get_match_detail_context(match):

    # ================= GOALS =================
    goals_qs = AttemptToGoal.objects.filter(
        match=match,
        outcome='On Target Goal'
    ).select_related('player', 'team', 'assist_by')

    own_goals_qs = AttemptToGoal.objects.filter(
        match=match,
        is_own_goal=True
    ).select_related('player', 'team')

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
            team_name = "Unknown"

        goals.append({
            'minute': goal.minute,
            'second': goal.second,
            'scorer': goal.player.name if goal.player else "Unknown",
            'assist_by': goal.assist_by.name if goal.assist_by else None,
            'is_own_goal': False,
            'team_name': team_name,
        })

    for og in own_goals_qs:
        if og.team_id == match.home_team_id:
            away_goals += 1
            scoring_team_name = match.away_team.name
        elif og.team_id == match.away_team_id:
            home_goals += 1
            scoring_team_name = match.home_team.name
        else:
            scoring_team_name = "Unknown"

        goals.append({
            'minute': og.minute,
            'second': og.second,
            'scorer': og.player.name if og.player else "Unknown",
            'assist_by': None,
            'is_own_goal': True,
            'team_name': scoring_team_name,
        })

    # ================= LINEUPS =================
    def prepare_lineup(team, mirror=False):
        players = MatchLineup.objects.filter(
            match=match, team=team, is_starting=True
        ).select_related("player")

        lineup = []
        for ml in players:
            coords = POSITION_COORDS.get(ml.position, {"top": 50, "left": 50})
            top = 100 - coords["top"] if mirror else coords["top"]

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

    # ================= PASS NETWORK =================
    home_pass_context = get_pass_network_context(match, match.home_team.id)
    away_pass_context = get_pass_network_context(match, match.away_team.id)

    home_total_passes = home_pass_context['total_passes']
    home_ball_lost = home_pass_context['ball_lost']
    away_total_passes = away_pass_context['total_passes']
    away_ball_lost = away_pass_context['ball_lost']

    # ================= PLAYER STATS =================
    all_players = MatchLineup.objects.filter(match=match).select_related("player", "team")
    player_stats = []

    for ml in all_players:
        player = ml.player
        pid = player.id

        shots = AttemptToGoal.objects.filter(match=match, player=player)
        goals_count = shots.filter(outcome='On Target Goal').count()
        shots_on = shots.filter(outcome__in=['On Target Goal', 'On Target Miss']).count()
        assists = AttemptToGoal.objects.filter(match=match, assist_by=player).count()

        if ml.team_id == match.home_team_id:
            total = home_total_passes.get(pid, 0)
            lost = home_ball_lost.get(pid, 0)
        else:
            total = away_total_passes.get(pid, 0)
            lost = away_ball_lost.get(pid, 0)

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
            'yellow_card': getattr(ml, 'yellow_card', 0),
            'red_card': getattr(ml, 'red_card', 0),
            'total_passes': total,
            'ball_lost': lost,
            'pass_accuracy': accuracy,
        })

    # ================= TEAM PASS STATS =================
    def calculate_team_passing(player_ids, totals, losts):
        return {
            'total_passes': sum(totals.get(pid, 0) for pid in player_ids),
            'ball_lost': sum(losts.get(pid, 0) for pid in player_ids),
        }

    home_pass_stats = calculate_team_passing(home_player_ids, home_total_passes, home_ball_lost)
    away_pass_stats = calculate_team_passing(away_player_ids, away_total_passes, away_ball_lost)

    # ================= ADMIN FLAGS (🔥 FIX) =================
    home_lineup_exists = MatchLineup.objects.filter(match=match, team=match.home_team).exists()
    away_lineup_exists = MatchLineup.objects.filter(match=match, team=match.away_team).exists()
    has_gps_data = GPSRecord.objects.filter(match=match).exists()

    return {
        'lineup': lineup,
        'home_lineup': home_lineup,
        'away_lineup': away_lineup,
        'home_team_goals': home_goals,
        'away_team_goals': away_goals,
        'player_stats': player_stats,
        'goals': goals,

        'home_pass_context': home_pass_context,
        'away_pass_context': away_pass_context,
        'home_pass_stats': home_pass_stats,
        'away_pass_stats': away_pass_stats,

        # ⭐ THIS FIXES YOUR PROBLEM
        'home_lineup_exists': home_lineup_exists,
        'away_lineup_exists': away_lineup_exists,
        'has_gps_data': has_gps_data,
    }