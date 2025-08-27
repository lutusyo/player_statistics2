# reports_app/views/match_summary_stats.py
from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Sum, F
from matches_app.models import Match
from tagging_app.models import AttemptToGoal, PassEvent
from lineup_app.models import MatchLineup, Substitution
from defensive_app.models import PlayerDefensiveStats  # optional
from teams_app.models import Team
from gps_app.models import GPSRecord  # added for distance data

def safe_div(a, b):
    try:
        return (a / b) * 100 if b else 0
    except Exception:
        return 0

def match_summary_stats_view(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    home = match.home_team
    away = match.away_team

    # --- Goals & Attempts ---
    all_attempts = AttemptToGoal.objects.filter(match=match)
    home_goals = all_attempts.filter(team=home, outcome='On Target Goal').count()
    away_goals = all_attempts.filter(team=away, outcome='On Target Goal').count()

    home_attempts_total = all_attempts.filter(team=home).count()
    away_attempts_total = all_attempts.filter(team=away).count()

    home_on_target = all_attempts.filter(team=home).filter(
        Q(outcome='On Target Goal') | Q(outcome='On Target Saved')
    ).count()
    away_on_target = all_attempts.filter(team=away).filter(
        Q(outcome='On Target Goal') | Q(outcome='On Target Saved')
    ).count()

    # --- Passes ---
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

    # --- Possession approximation ---
    possession_home_pct = safe_div(home_pass_completed, total_completed) if total_completed else safe_div(home_pass_count, total_passes)
    possession_away_pct = 100 - possession_home_pct

    # --- Crosses ---
    home_crosses = all_attempts.filter(team=home, delivery_type='Cross').count()
    away_crosses = all_attempts.filter(team=away, delivery_type='Cross').count()

    # --- Receptions in Final Third ---
    home_receptions_final_third = PassEvent.objects.filter(match=match, to_team=home, x_end__gte=66).count()
    away_receptions_final_third = PassEvent.objects.filter(match=match, to_team=away, x_end__lte=34).count()

    # --- Ball Progressions ---
    home_ball_progressions = PassEvent.objects.filter(
        match=match, from_team=home, x_start__isnull=False, x_end__isnull=False
    ).filter(x_end__gt=F('x_start') + 10).count()
    away_ball_progressions = PassEvent.objects.filter(
        match=match, from_team=away, x_start__isnull=False, x_end__isnull=False
    ).filter(x_end__gt=F('x_start') + 10).count()

    # --- Defensive stats ---
    try:
        home_def_stats = PlayerDefensiveStats.objects.filter(match=match, player__team=home)
        away_def_stats = PlayerDefensiveStats.objects.filter(match=match, player__team=away)

        home_forced_turnovers = home_def_stats.aggregate(total=Sum('foul_won'))['total'] or 0
        away_forced_turnovers = away_def_stats.aggregate(total=Sum('foul_won'))['total'] or 0

        home_def_pressures = (home_def_stats.aggregate(t=Sum('tackle_won'))['t'] or 0) + \
                             (home_def_stats.aggregate(a=Sum('physical_duel_won'))['a'] or 0)
        away_def_pressures = (away_def_stats.aggregate(t=Sum('tackle_won'))['t'] or 0) + \
                             (away_def_stats.aggregate(a=Sum('physical_duel_won'))['a'] or 0)
    except Exception:
        home_forced_turnovers = away_forced_turnovers = 0
        home_def_pressures = away_def_pressures = 0

    # --- GPS Stats ---
    home_distance = GPSRecord.objects.filter(match=match, player__team=home).aggregate(
        total_distance=Sum('distance')
    )['total_distance'] or 0.0

    away_distance = GPSRecord.objects.filter(match=match, player__team=away).aggregate(
        total_distance=Sum('distance')
    )['total_distance'] or 0.0

    home_zone4_sprint_km = GPSRecord.objects.filter(match=match, player__team=home).aggregate(
        total_distance=Sum('hi_distance')
    )['total_distance'] or 0.0

    away_zone4_sprint_km = GPSRecord.objects.filter(match=match, player__team=away).aggregate(
        total_distance=Sum('hi_distance')
    )['total_distance'] or 0.0

    # --- Other placeholders ---
    home_completed_line_breaks = away_completed_line_breaks = 0
    home_defensive_line_breaks = away_defensive_line_breaks = 0
    home_second_balls = away_second_balls = 0

    # --- Stats list for template ---
    stats = [
        {'label': 'Goals', 'home': home_goals, 'away': away_goals, 'home_val': home_goals, 'away_val': away_goals},
        {'label': 'Attempts at Goal (On Target)', 'home': f"{home_attempts_total} ({home_on_target})",
         'away': f"{away_attempts_total} ({away_on_target})", 'home_val': home_on_target, 'away_val': away_on_target},
        {'label': 'Total Passes (Complete)', 'home': f"{home_pass_count} ({home_pass_completed})",
         'away': f"{away_pass_count} ({away_pass_completed})", 'home_val': home_pass_completed, 'away_val': away_pass_completed},
        {'label': 'Pass Completion %', 'home': f"{home_pass_pct:.1f}%", 'away': f"{away_pass_pct:.1f}%",
         'home_val': home_pass_pct, 'away_val': away_pass_pct},
        {'label': 'Completed Line Breaks', 'home': home_completed_line_breaks, 'away': away_completed_line_breaks,
         'home_val': home_completed_line_breaks, 'away_val': away_completed_line_breaks},
        {'label': 'Defensive Line Breaks', 'home': home_defensive_line_breaks, 'away': away_defensive_line_breaks,
         'home_val': home_defensive_line_breaks, 'away_val': away_defensive_line_breaks},
        {'label': 'Receptions in Final Third', 'home': home_receptions_final_third, 'away': away_receptions_final_third,
         'home_val': home_receptions_final_third, 'away_val': away_receptions_final_third},
        {'label': 'Crosses', 'home': home_crosses, 'away': away_crosses, 'home_val': home_crosses, 'away_val': away_crosses},
        {'label': 'Ball Progressions', 'home': home_ball_progressions, 'away': away_ball_progressions,
         'home_val': home_ball_progressions, 'away_val': away_ball_progressions},
        {'label': 'Defensive Pressures', 'home': home_def_pressures, 'away': away_def_pressures,
         'home_val': home_def_pressures, 'away_val': away_def_pressures},
        {'label': 'Forced Turnovers', 'home': home_forced_turnovers, 'away': away_forced_turnovers,
         'home_val': home_forced_turnovers, 'away_val': away_forced_turnovers},
        {'label': 'Second Balls', 'home': home_second_balls, 'away': away_second_balls,
         'home_val': home_second_balls, 'away_val': away_second_balls},
        {'label': 'Total Distance Covered', 'home': f"{home_distance/1000:.1f} km", 'away': f"{away_distance/1000:.1f} km",
         'home_val': home_distance, 'away_val': away_distance},
        {'label': 'Zone 4 - Low Speed Sprinting', 'home': f"{home_zone4_sprint_km/1000:.1f} km",
         'away': f"{away_zone4_sprint_km/1000:.1f} km", 'home_val': home_zone4_sprint_km, 'away_val': away_zone4_sprint_km},
    ]

    context = {
    'match': match,
    'home': home,
    'away': away,
    'home_score': home_goals,   # <-- add this
    'away_score': away_goals,   # <-- add this
    'possession_home_pct': round(possession_home_pct, 1),
    'possession_away_pct': round(possession_away_pct, 1),
    'stats': stats,
}
    
    

    return render(request, 'reports_app/match_summary_stats.html', context)
