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
    # Count passes where possession is regained by your team after opponent pass
    recoveries = PassEvent.objects.filter(
        match=match,
        to_team=team,
        is_possession_regained=True
    ).exclude(from_team=team).count()
    return recoveries

def get_match_stats(match):
    home = match.home_team
    away = match.away_team

    # --- Goal-related events ---
    all_attempts = AttemptToGoal.objects.filter(match=match)

    home_goals = all_attempts.filter(team=home, outcome='On Target Goal').count()
    away_goals = all_attempts.filter(team=away, outcome='On Target Goal').count()

    home_attempts_total = all_attempts.filter(team=home).count()
    away_attempts_total = all_attempts.filter(team=away).count()

    home_on_target = all_attempts.filter(team=home, outcome__in=['On Target Goal', 'On Target Saved']).count()
    away_on_target = all_attempts.filter(team=away, outcome__in=['On Target Goal', 'On Target Saved']).count()

    home_assists = all_attempts.filter(team=home, outcome='On Target Goal', assist_by__isnull=False).count()
    away_assists = all_attempts.filter(team=away, outcome='On Target Goal', assist_by__isnull=False).count()

    home_crosses = all_attempts.filter(team=home, delivery_type='Cross').count()
    away_crosses = all_attempts.filter(team=away, delivery_type='Cross').count()

    # --- Pass-related events ---
    home_passes = PassEvent.objects.filter(match=match, from_team=home)
    away_passes = PassEvent.objects.filter(match=match, from_team=away)

    home_pass_count = home_passes.count()
    away_pass_count = away_passes.count()

    home_pass_completed = home_passes.filter(is_successful=True).count()
    away_pass_completed = away_passes.filter(is_successful=True).count()

    total_passes = home_pass_count + away_pass_count
    total_completed = home_pass_completed + away_pass_completed

    home_pass_pct = safe_div(home_pass_completed, home_pass_count)
    away_pass_pct = safe_div(away_pass_completed, away_pass_count)

    possession_home_pct = safe_div(home_pass_completed, total_completed) if total_completed else safe_div(home_pass_count, total_passes)
    possession_away_pct = 100 - possession_home_pct

    home_receptions_final_third = PassEvent.objects.filter(match=match, to_team=home, x_end__gte=66).count()
    away_receptions_final_third = PassEvent.objects.filter(match=match, to_team=away, x_end__lte=34).count()

    home_ball_progressions = home_passes.filter(
        x_start__isnull=False, x_end__isnull=False
    ).filter(x_end__gt=F('x_start') + 10).count()

    away_ball_progressions = away_passes.filter(
        x_start__isnull=False, x_end__isnull=False
    ).filter(x_end__gt=F('x_start') + 10).count()

    # --- Defensive stats ---
    home_def_stats = PlayerDefensiveStats.objects.filter(match=match, player__team=home)
    away_def_stats = PlayerDefensiveStats.objects.filter(match=match, player__team=away)

    def get_defensive_agg(qs, field):
        return qs.aggregate(val=Sum(field))['val'] or 0

    home_forced_turnovers = get_defensive_agg(home_def_stats, 'foul_won')
    away_forced_turnovers = get_defensive_agg(away_def_stats, 'foul_won')

    home_def_pressures = get_defensive_agg(home_def_stats, 'tackle_won') + get_defensive_agg(home_def_stats, 'physical_duel_won')
    away_def_pressures = get_defensive_agg(away_def_stats, 'tackle_won') + get_defensive_agg(away_def_stats, 'physical_duel_won')

    home_completed_line_breaks = get_defensive_agg(home_def_stats, 'line_breaks_completed')
    away_completed_line_breaks = get_defensive_agg(away_def_stats, 'line_breaks_completed')

    home_defensive_line_breaks = get_defensive_agg(home_def_stats, 'defensive_line_breaks')
    away_defensive_line_breaks = get_defensive_agg(away_def_stats, 'defensive_line_breaks')

    # Use passing network to get second ball recoveries (possession regained from opponent pass)
    home_second_balls = get_second_ball_recoveries(match, home)
    away_second_balls = get_second_ball_recoveries(match, away)

    # --- GPS data ---
    home_gps = GPSRecord.objects.filter(match=match, player__team=home)
    away_gps = GPSRecord.objects.filter(match=match, player__team=away)

    home_distance = home_gps.aggregate(total=Sum('distance'))['total'] or 0.0
    away_distance = away_gps.aggregate(total=Sum('distance'))['total'] or 0.0

    home_zone4_sprint_km = home_gps.aggregate(total=Sum('hi_distance'))['total'] or 0.0
    away_zone4_sprint_km = away_gps.aggregate(total=Sum('hi_distance'))['total'] or 0.0

    # --- Lineups & Substitutions ---
    home_starting = MatchLineup.objects.filter(match=match, team=home, is_starting=True)
    home_subs = MatchLineup.objects.filter(match=match, team=home, is_starting=False)
    away_starting = MatchLineup.objects.filter(match=match, team=away, is_starting=True)
    away_subs = MatchLineup.objects.filter(match=match, team=away, is_starting=False)

    home_substitutions = Substitution.objects.filter(match=match, player_in__team=home)
    away_substitutions = Substitution.objects.filter(match=match, player_in__team=away)

    stats = [
        {'label': 'Goals', 'home': home_goals, 'away': away_goals},
        {'label': 'Assists (On Target Goals)', 'home': home_assists, 'away': away_assists},
        {'label': 'Attempts at Goal (On Target)', 'home': f"{home_attempts_total} ({home_on_target})",
         'away': f"{away_attempts_total} ({away_on_target})"},
        {'label': 'Total Passes (Complete)', 'home': f"{home_pass_count} ({home_pass_completed})",
         'away': f"{away_pass_count} ({away_pass_completed})"},
        {'label': 'Pass Completion %', 'home': f"{home_pass_pct:.1f}%", 'away': f"{away_pass_pct:.1f}%"},
        {'label': 'Completed Line Breaks', 'home': home_completed_line_breaks, 'away': away_completed_line_breaks},
        {'label': 'Defensive Line Breaks', 'home': home_defensive_line_breaks, 'away': away_defensive_line_breaks},
        {'label': 'Receptions in Final Third', 'home': home_receptions_final_third, 'away': away_receptions_final_third},
        {'label': 'Crosses', 'home': home_crosses, 'away': away_crosses},
        {'label': 'Ball Progressions', 'home': home_ball_progressions, 'away': away_ball_progressions},
        {'label': 'Defensive Pressures', 'home': home_def_pressures, 'away': away_def_pressures},
        {'label': 'Forced Turnovers', 'home': home_forced_turnovers, 'away': away_forced_turnovers},
        {'label': 'Second Balls', 'home': home_second_balls, 'away': away_second_balls},
        {'label': 'Total Distance Covered', 'home': f"{home_distance / 1000:.1f} km", 'away': f"{away_distance / 1000:.1f} km"},
        {'label': 'Zone 4 - Low Speed Sprinting', 'home': f"{home_zone4_sprint_km / 1000:.1f} km", 'away': f"{away_zone4_sprint_km / 1000:.1f} km"},
    ]

    return {
        'match': match,
        'home': home,
        'away': away,
        'home_goals': home_goals,
        'away_goals': away_goals,
        'home_starting': home_starting,
        'home_subs': home_subs,
        'away_starting': away_starting,
        'away_subs': away_subs,
        'home_substitutions': home_substitutions,
        'away_substitutions': away_substitutions,
        'possession_home_pct': round(possession_home_pct, 1),
        'possession_away_pct': round(possession_away_pct, 1),
        'stats': stats,
        'pass_events': PassEvent.objects.filter(match=match),  # used for charts etc.
    }
