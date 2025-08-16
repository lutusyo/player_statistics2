# reports_app/views/match_summary_stats.py
from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Q, Sum, F
from matches_app.models import Match
from lineup_app.models import MatchLineup, Substitution
from tagging_app.models import AttemptToGoal, PassEvent, GoalkeeperDistributionEvent  # adjust import path if needed
from defensive_app.models import PlayerDefensiveStats  # if in other app adjust or remove
from teams_app.models import Team

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

    home_attempts_total = AttemptToGoal.objects.filter(match=match, team=home).count()
    away_attempts_total = AttemptToGoal.objects.filter(match=match, team=away).count()

    home_on_target = all_attempts.filter(match=match, team=home).filter(
        Q(outcome='On Target Goal') | Q(outcome='On Target Saved')
    ).count()
    away_on_target = all_attempts.filter(match=match, team=away).filter(
        Q(outcome='On Target Goal') | Q(outcome='On Target Saved')
    ).count()

    # --- Passes & completion ---
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

    # A simple possession approximation: % of completed passes
    # NOTE: Replace with your accurate possession source if you have it
    possession_home_pct = safe_div(home_pass_completed, total_completed) if total_completed else safe_div(home_pass_count, total_passes)
    possession_away_pct = 100 - possession_home_pct if possession_home_pct else safe_div(away_pass_count, total_passes)

    # --- Crosses (heuristic) ---
    # We don't have a dedicated 'Cross' event model in PassEvent, but AttemptToGoal.delivery_type may show crosses
    home_crosses = AttemptToGoal.objects.filter(match=match, team=home, delivery_type='Cross').count()
    away_crosses = AttemptToGoal.objects.filter(match=match, team=away, delivery_type='Cross').count()

    # --- Receptions in final third (heuristic)
    # If PassEvent has x_end in 0-100 (pitch), treat >66 as final third
    home_receptions_final_third = PassEvent.objects.filter(match=match, to_team=home, x_end__gte=66).count()
    away_receptions_final_third = PassEvent.objects.filter(match=match, to_team=away, x_end__lte=34).count()  # if pitch mirrored, adjust as needed

    # --- Ball progressions (heuristic) ---
    # Count passes that move forward by threshold (x_end - x_start) > 10
    home_ball_progressions = PassEvent.objects.filter(match=match, from_team=home, x_start__isnull=False, x_end__isnull=False).filter(x_end__gt=F('x_start') + 10).count()
    away_ball_progressions = PassEvent.objects.filter(match=match, from_team=away, x_start__isnull=False, x_end__isnull=False).filter(x_end__gt=F('x_start') + 10).count()

    # --- Defensive pressures / forced turnovers / second balls ---
    # If you have PlayerDefensiveStats or a PressEvent model, use that. We'll try a fallback using PlayerDefensiveStats fields if present.
    try:
        home_def_stats = PlayerDefensiveStats.objects.filter(match=match, player__team=home)
        away_def_stats = PlayerDefensiveStats.objects.filter(match=match, player__team=away)

        home_forced_turnovers = home_def_stats.aggregate(total=Sum('foul_won'))['total'] or 0
        away_forced_turnovers = away_def_stats.aggregate(total=Sum('foul_won'))['total'] or 0

        # use tackles+duels as proxies for pressures applied
        home_def_pressures = (home_def_stats.aggregate(t=Sum('tackle_won'))['t'] or 0) + (home_def_stats.aggregate(a=Sum('physical_duel_won'))['a'] or 0)
        away_def_pressures = (away_def_stats.aggregate(t=Sum('tackle_won'))['t'] or 0) + (away_def_stats.aggregate(a=Sum('physical_duel_won'))['a'] or 0)
    except Exception:
        home_forced_turnovers = away_forced_turnovers = 0
        home_def_pressures = away_def_pressures = 0

    # --- Total distance & sprint distance ---
    # You mentioned GPS pods; if you have GPS data model (not shown here) replace below with real aggregation.
    # For now: placeholder values or 0
    home_distance = 0.0
    away_distance = 0.0
    home_zone4_sprint_km = 0.0
    away_zone4_sprint_km = 0.0

    # --- Completed Line Breaks & Defensive Line Breaks ---
    # If you have a metric or event, use it; otherwise set placeholder 0
    home_completed_line_breaks = 0
    away_completed_line_breaks = 0
    home_defensive_line_breaks = 0
    away_defensive_line_breaks = 0

    # --- Forced second balls (placeholder) ---
    home_second_balls = 0
    away_second_balls = 0

    # Build stats list in the order you want them displayed
    stats = [
        {
            'label': 'Goals',
            'home': home_goals,
            'away': away_goals,
            'fmt': 'int'
        },
        {
            'label': 'Attempts at Goal (On Target)',
            'home': f"{home_attempts_total} ({home_on_target})",
            'away': f"{away_attempts_total} ({away_on_target})",
            'home_val': home_on_target,
            'away_val': away_on_target,
            'fmt': 'text'
        },
        {
            'label': 'Total Passes (Complete)',
            'home': f"{home_pass_count} ({home_pass_completed})",
            'away': f"{away_pass_count} ({away_pass_completed})",
            'home_val': home_pass_completed,
            'away_val': away_pass_completed,
            'fmt': 'text'
        },
        {
            'label': 'Pass Completion %',
            'home': f"{home_pass_pct:.1f} %",
            'away': f"{away_pass_pct:.1f} %",
            'home_val': home_pass_pct,
            'away_val': away_pass_pct,
            'fmt': 'pct'
        },
        {
            'label': 'Completed Line Breaks',
            'home': home_completed_line_breaks,
            'away': away_completed_line_breaks,
            'home_val': home_completed_line_breaks,
            'away_val': away_completed_line_breaks,
            'fmt': 'int'
        },
        {
            'label': 'Defensive Line Breaks',
            'home': home_defensive_line_breaks,
            'away': away_defensive_line_breaks,
            'home_val': home_defensive_line_breaks,
            'away_val': away_defensive_line_breaks,
            'fmt': 'int'
        },
        {
            'label': 'Receptions in the Final Third',
            'home': home_receptions_final_third,
            'away': away_receptions_final_third,
            'home_val': home_receptions_final_third,
            'away_val': away_receptions_final_third,
            'fmt': 'int'
        },
        {
            'label': 'Crosses',
            'home': home_crosses,
            'away': away_crosses,
            'home_val': home_crosses,
            'away_val': away_crosses,
            'fmt': 'int'
        },
        {
            'label': 'Ball Progressions',
            'home': home_ball_progressions,
            'away': away_ball_progressions,
            'home_val': home_ball_progressions,
            'away_val': away_ball_progressions,
            'fmt': 'int'
        },
        {
            'label': 'Defensive Pressures Applied (Direct Pressures)',
            'home': home_def_pressures,
            'away': away_def_pressures,
            'home_val': home_def_pressures,
            'away_val': away_def_pressures,
            'fmt': 'int'
        },
        {
            'label': 'Forced Turnovers',
            'home': home_forced_turnovers,
            'away': away_forced_turnovers,
            'home_val': home_forced_turnovers,
            'away_val': away_forced_turnovers,
            'fmt': 'int'
        },
        {
            'label': 'Second Balls',
            'home': home_second_balls,
            'away': away_second_balls,
            'home_val': home_second_balls,
            'away_val': away_second_balls,
            'fmt': 'int'
        },
        {
            'label': 'Total Distance Covered',
            'home': f"{home_distance:.1f} km",
            'away': f"{away_distance:.1f} km",
            'home_val': home_distance,
            'away_val': away_distance,
            'fmt': 'text'
        },
        {
            'label': 'Zone 4 - Low Speed Sprinting: 20-25 km/h',
            'home': f"{home_zone4_sprint_km:.1f} km",
            'away': f"{away_zone4_sprint_km:.1f} km",
            'home_val': home_zone4_sprint_km,
            'away_val': away_zone4_sprint_km,
            'fmt': 'text'
        },
    ]

    context = {
        'match': match,
        'home': home,
        'away': away,
        'possession_home_pct': round(possession_home_pct, 1),
        'possession_away_pct': round(possession_away_pct, 1),
        'stats': stats
    }
    return render(request, 'reports_app/match_summary_stats.html', context)
