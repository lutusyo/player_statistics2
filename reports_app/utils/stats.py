from django.db.models import Q, Sum, F, Count
from tagging_app.models import AttemptToGoal, PassEvent
from defensive_app.models import PlayerDefensiveStats
from gps_app.models import GPSRecord
from lineup_app.models import MatchLineup, Substitution

def safe_div(a, b):
    try:
        return (a / b) * 100 if b else 0
    except Exception:
        return 0

def get_second_ball_recoveries(match, team):
    return PassEvent.objects.filter(
        match=match,
        to_team=team,
        is_possession_regained=True
    ).exclude(from_team=team).count()


def get_match_stats(match):
    # Determine teams based on AttemptToGoal data
    our_attempt = AttemptToGoal.objects.filter(match=match, is_opponent=False).first()
    opponent_attempt = AttemptToGoal.objects.filter(match=match, is_opponent=True).first()

    our_team = our_attempt.team if our_attempt else match.home_team
    opponent_team = opponent_attempt.team if opponent_attempt else match.away_team

    # --- Goal-related events ---
    all_attempts = AttemptToGoal.objects.filter(match=match)

    our_goals = all_attempts.filter(team=our_team, outcome='On Target Goal', is_own_goal=False).count()
    opponent_goals = all_attempts.filter(team=opponent_team, outcome='On Target Goal', is_own_goal=False).count()

    our_attempts_total = all_attempts.filter(team=our_team).count()
    opponent_attempts_total = all_attempts.filter(team=opponent_team).count()

    our_on_target = all_attempts.filter(team=our_team, outcome__in=['On Target Goal', 'On Target Saved']).count()
    opponent_on_target = all_attempts.filter(team=opponent_team, outcome__in=['On Target Goal', 'On Target Saved']).count()

    our_assists = all_attempts.filter(team=our_team, outcome='On Target Goal', assist_by__isnull=False).count()
    opponent_assists = all_attempts.filter(team=opponent_team, outcome='On Target Goal', assist_by__isnull=False).count()

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

    our_pass_pct = safe_div(our_pass_completed, our_pass_count)
    opponent_pass_pct = safe_div(opponent_pass_completed, opponent_pass_count)

    possession_our_pct = safe_div(our_pass_completed, total_completed) if total_completed else safe_div(our_pass_count, total_passes)
    possession_opponent_pct = 100 - possession_our_pct

    our_receptions_final_third = PassEvent.objects.filter(match=match, to_team=our_team, x_end__gte=66).count()
    opponent_receptions_final_third = PassEvent.objects.filter(match=match, to_team=opponent_team, x_end__lte=34).count()

    our_ball_progressions = our_passes.filter(
        x_start__isnull=False, x_end__isnull=False
    ).filter(x_end__gt=F('x_start') + 10).count()

    opponent_ball_progressions = opponent_passes.filter(
        x_start__isnull=False, x_end__isnull=False
    ).filter(x_end__gt=F('x_start') + 10).count()

    # --- Defensive stats ---
    our_def_stats = PlayerDefensiveStats.objects.filter(match=match, player__team=our_team)
    opponent_def_stats = PlayerDefensiveStats.objects.filter(match=match, player__team=opponent_team)

    def get_defensive_agg(qs, field):
        return qs.aggregate(val=Sum(field))['val'] or 0

    our_forced_turnovers = get_defensive_agg(our_def_stats, 'foul_won')
    opponent_forced_turnovers = get_defensive_agg(opponent_def_stats, 'foul_won')

    our_def_pressures = get_defensive_agg(our_def_stats, 'tackle_won') + get_defensive_agg(our_def_stats, 'physical_duel_won')
    opponent_def_pressures = get_defensive_agg(opponent_def_stats, 'tackle_won') + get_defensive_agg(opponent_def_stats, 'physical_duel_won')

    our_completed_line_breaks = get_defensive_agg(our_def_stats, 'line_breaks_completed')
    opponent_completed_line_breaks = get_defensive_agg(opponent_def_stats, 'line_breaks_completed')

    our_defensive_line_breaks = get_defensive_agg(our_def_stats, 'defensive_line_breaks')
    opponent_defensive_line_breaks = get_defensive_agg(opponent_def_stats, 'defensive_line_breaks')

    # --- Second Ball Recoveries ---
    our_second_balls = get_second_ball_recoveries(match, our_team)
    opponent_second_balls = get_second_ball_recoveries(match, opponent_team)

    # --- GPS data ---
    our_gps = GPSRecord.objects.filter(match=match, player__team=our_team)
    opponent_gps = GPSRecord.objects.filter(match=match, player__team=opponent_team)

    our_distance = our_gps.aggregate(total=Sum('distance'))['total'] or 0.0
    opponent_distance = opponent_gps.aggregate(total=Sum('distance'))['total'] or 0.0

    our_zone4_sprint_km = our_gps.aggregate(total=Sum('hi_distance'))['total'] or 0.0
    opponent_zone4_sprint_km = opponent_gps.aggregate(total=Sum('hi_distance'))['total'] or 0.0

    # --- Lineups & Substitutions ---
    our_starting = MatchLineup.objects.filter(match=match, team=our_team, is_starting=True)
    our_subs = MatchLineup.objects.filter(match=match, team=our_team, is_starting=False)

    opponent_starting = MatchLineup.objects.filter(match=match, team=opponent_team, is_starting=True)
    opponent_subs = MatchLineup.objects.filter(match=match, team=opponent_team, is_starting=False)

    our_substitutions = Substitution.objects.filter(match=match, player_in__team=our_team)
    opponent_substitutions = Substitution.objects.filter(match=match, player_in__team=opponent_team)

    stats = [
        {'label': 'Goals', 'home': our_goals, 'away': opponent_goals},
        {'label': 'Assists (On Target Goals)', 'home': our_assists, 'away': opponent_assists},
        {'label': 'Attempts at Goal (On Target)', 'home': f"{our_attempts_total} ({our_on_target})", 'away': f"{opponent_attempts_total} ({opponent_on_target})"},
        {'label': 'Total Passes (Complete)', 'home': f"{our_pass_count} ({our_pass_completed})", 'away': f"{opponent_pass_count} ({opponent_pass_completed})"},
        {'label': 'Pass Completion %', 'home': f"{our_pass_pct:.1f}%", 'away': f"{opponent_pass_pct:.1f}%"},
        {'label': 'Completed Line Breaks', 'home': our_completed_line_breaks, 'away': opponent_completed_line_breaks},
        {'label': 'Defensive Line Breaks', 'home': our_defensive_line_breaks, 'away': opponent_defensive_line_breaks},
        {'label': 'Receptions in Final Third', 'home': our_receptions_final_third, 'away': opponent_receptions_final_third},
        {'label': 'Crosses', 'home': our_crosses, 'away': opponent_crosses},
        {'label': 'Ball Progressions', 'home': our_ball_progressions, 'away': opponent_ball_progressions},
        {'label': 'Defensive Pressures', 'home': our_def_pressures, 'away': opponent_def_pressures},
        {'label': 'Forced Turnovers', 'home': our_forced_turnovers, 'away': opponent_forced_turnovers},
        {'label': 'Second Balls', 'home': our_second_balls, 'away': opponent_second_balls},
        {'label': 'Total Distance Covered', 'home': f"{our_distance / 1000:.1f} km", 'away': f"{opponent_distance / 1000:.1f} km"},
        {'label': 'Zone 4 - Low Speed Sprinting', 'home': f"{our_zone4_sprint_km / 1000:.1f} km", 'away': f"{opponent_zone4_sprint_km / 1000:.1f} km"},
    ]

    return {
        'match': match,
        'our_team': our_team,
        'opponent_team': opponent_team,
        'home_goals': our_goals,
        'away_goals': opponent_goals,
        'our_starting': our_starting,
        'our_subs': our_subs,
        'opponent_starting': opponent_starting,
        'opponent_subs': opponent_subs,
        'our_substitutions': our_substitutions,
        'opponent_substitutions': opponent_substitutions,
        'possession_home_pct': round(possession_our_pct, 1),
        'possession_away_pct': round(possession_opponent_pct, 1),
        'stats': stats,
        'pass_events': PassEvent.objects.filter(match=match),
    }
