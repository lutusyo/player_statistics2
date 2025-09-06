from django.db.models import Q, Sum, F, Count
from tagging_app.models import AttemptToGoal, PassEvent
from defensive_app.models import PlayerDefensiveStats
from gps_app.models import GPSRecord
from lineup_app.models import MatchLineup, Substitution


def safe_div(numerator, denominator):
    try:
        return (numerator / denominator) * 100 if denominator else 0
    except (ZeroDivisionError, TypeError):
        return 0

def get_second_ball_recoveries(match, team):
    # TODO: Replace this with actual logic to calculate second ball recoveries
    return 0



def get_match_stats(match):
    # Get teams based on AttemptToGoal data
    our_attempt = AttemptToGoal.objects.filter(match=match, is_opponent=False).first()
    opponent_attempt = AttemptToGoal.objects.filter(match=match, is_opponent=True).first()

    our_team = our_attempt.team if our_attempt else match.home_team
    opponent_team = opponent_attempt.team if opponent_attempt else match.away_team

    # --- Goal-related events ---
    all_attempts = AttemptToGoal.objects.filter(match=match)

    # Goals for each team
    our_goals = all_attempts.filter(team=our_team, outcome='On Target Goal', is_own_goal=False).count()
    opponent_goals = all_attempts.filter(team=opponent_team, outcome='On Target Goal', is_own_goal=False).count()

    # Attempt stats
    our_attempts_total = all_attempts.filter(team=our_team).count()
    opponent_attempts_total = all_attempts.filter(team=opponent_team).count()

    # On target attempts
    our_on_target = all_attempts.filter(team=our_team, outcome__in=['On Target Goal', 'On Target Saved']).count()
    opponent_on_target = all_attempts.filter(team=opponent_team, outcome__in=['On Target Goal', 'On Target Saved']).count()

    # Assists
    our_assists = all_attempts.filter(team=our_team, outcome='On Target Goal', assist_by__isnull=False).count()
    opponent_assists = all_attempts.filter(team=opponent_team, outcome='On Target Goal', assist_by__isnull=False).count()

    # Crosses
    our_crosses = all_attempts.filter(team=our_team, delivery_type='Cross').count()
    opponent_crosses = all_attempts.filter(team=opponent_team, delivery_type='Cross').count()

    # --- Pass-related events ---
    our_passes = PassEvent.objects.filter(match=match, from_team=our_team)
    opponent_passes = PassEvent.objects.filter(match=match, from_team=opponent_team)

    our_pass_count = our_passes.count()
    opponent_pass_count = opponent_passes.count()

    our_pass_completed = our_passes.filter(is_successful=True).count()
    opponent_pass_completed = opponent_passes.filter(is_successful=True).count()

    total_passes = our_pass_count + opponent_pass_count
    total_completed = our_pass_completed + opponent_pass_completed

    # Calculate pass completion percentages
    our_pass_pct = safe_div(our_pass_completed, our_pass_count)
    opponent_pass_pct = safe_div(opponent_pass_completed, opponent_pass_count)

    # Possession calculation
    possession_our_pct = safe_div(our_pass_completed, total_completed) if total_completed else safe_div(our_pass_count, total_passes)
    possession_opponent_pct = 100 - possession_our_pct

    # --- Second Ball Recoveries ---
    our_second_balls = get_second_ball_recoveries(match, our_team)
    opponent_second_balls = get_second_ball_recoveries(match, opponent_team)

    # --- GPS data ---
    our_gps = GPSRecord.objects.filter(match=match, player__team=our_team)
    opponent_gps = GPSRecord.objects.filter(match=match, player__team=opponent_team)

    # Total distance covered
    our_distance = our_gps.aggregate(total=Sum('distance'))['total'] or 0.0
    opponent_distance = opponent_gps.aggregate(total=Sum('distance'))['total'] or 0.0

    # Sprinting in Zone 4 (High-speed)
    our_zone4_sprint_km = our_gps.aggregate(total=Sum('hi_distance'))['total'] or 0.0
    opponent_zone4_sprint_km = opponent_gps.aggregate(total=Sum('hi_distance'))['total'] or 0.0

    # --- Stats to Display ---
    stats = [
        {'label': 'Goals', 'home': our_goals, 'away': opponent_goals},
        {'label': 'Assists (On Target Goals)', 'home': our_assists, 'away': opponent_assists},
        {'label': 'Attempts at Goal (On Target)', 'home': f"{our_attempts_total} ({our_on_target})", 'away': f"{opponent_attempts_total} ({opponent_on_target})"},
        {'label': 'Total Passes (Complete)', 'home': f"{our_pass_count} ({our_pass_completed})", 'away': f"{opponent_pass_count} ({opponent_pass_completed})"},
        {'label': 'Pass Completion %', 'home': f"{our_pass_pct:.1f}%", 'away': f"{opponent_pass_pct:.1f}%"},
        {'label': 'Second Balls', 'home': our_second_balls, 'away': opponent_second_balls},
        {'label': 'Total Distance Covered', 'home': f"{our_distance / 1000:.1f} km", 'away': f"{opponent_distance / 1000:.1f} km"},
        {'label': 'Zone 4 - Low Speed Sprinting', 'home': f"{our_zone4_sprint_km / 1000:.1f} km", 'away': f"{opponent_zone4_sprint_km / 1000:.1f} km"},
    ]

    return {
        'match': match,
        'home_team': our_team,
        'away_team': opponent_team,
        'home_goals': our_goals,
        'away_goals': opponent_goals,
        'possession_home_pct': round(possession_our_pct, 1),
        'possession_away_pct': round(possession_opponent_pct, 1),
        'stats': stats,
    }
