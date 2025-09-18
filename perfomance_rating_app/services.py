# perfomance_rating_app/services.py
from tagging_app.models import AttemptToGoal, PassEvent
from lineup_app.models import MatchLineup
from defensive_app.models import PlayerDefensiveStats
from perfomance_rating_app.models import PerformanceRating

def compute_player_rating(player, match):
    """
    Compute and persist a PerformanceRating for player in match.
    Returns the saved PerformanceRating instance.
    """
    # --- Attacking (shots/goals) ---
    attempts = AttemptToGoal.objects.filter(match=match, player=player)
    goals = attempts.filter(outcome='On Target Goal', is_own_goal=False).count()
    shots = attempts.count()
    attacking_score = min(5, goals + shots // 3)

    # --- Creativity (assists that resulted in goals + passes) ---
    assists = AttemptToGoal.objects.filter(
        match=match,
        assist_by=player,
        outcome='On Target Goal',
        is_own_goal=False
    ).count()
    passes = PassEvent.objects.filter(match=match, from_player=player).count()
    creativity_score = min(5, assists + passes // 10)

    # --- Defending (use defensive stats if present) ---
    try:
        d = PlayerDefensiveStats.objects.get(match=match, player=player)
        # prefer tackle success rate
        denom = (d.tackle_won + d.tackle_lost)
        if denom > 0:
            ratio = d.tackle_won / denom
            defending_score = min(5, max(1, round(ratio * 5)))
        else:
            # fallback to 1v1 defensive ratio
            denom2 = (d.duel_1v1_won_def + d.duel_1v1_lost_def)
            if denom2 > 0:
                ratio2 = d.duel_1v1_won_def / denom2
                defending_score = min(5, max(1, round(ratio2 * 5)))
            else:
                defending_score = 3
    except PlayerDefensiveStats.DoesNotExist:
        defending_score = 3

    # --- Tactical (minutes played as proxy) ---
    try:
        lu = MatchLineup.objects.get(match=match, player=player)
        # prefer the calculate_minutes_played API (final_minute fallback 90)
        final_minute = 90
        if hasattr(match, 'elapsed_minutes') and callable(getattr(match, 'elapsed_minutes')):
            try:
                final_minute = match.elapsed_minutes()
            except Exception:
                final_minute = 90
        minutes = lu.calculate_minutes_played(final_minute=final_minute) or lu.minutes_played or 0
        tactical_score = 1 if minutes == 0 else min(5, max(1, round(minutes / 18)))  # 90 -> 5
    except MatchLineup.DoesNotExist:
        tactical_score = 1

    # --- Technical (pass accuracy) ---
    total_passes = PassEvent.objects.filter(match=match, from_player=player).count()
    successful_passes = PassEvent.objects.filter(match=match, from_player=player, is_successful=True).count()
    if total_passes > 0:
        pass_accuracy = successful_passes / total_passes
        technical_score = min(5, max(1, round(pass_accuracy * 5)))
    else:
        technical_score = 2

    # --- Discipline (penalize fouls/yellows/reds) ---
    try:
        d = PlayerDefensiveStats.objects.get(match=match, player=player)
        # simple penalty model: red=3, yellow=1, every 4 fouls = 1 penalty point
        penalty = d.red_card * 3 + d.yellow_card * 1 + (d.foul_committed // 4)
        discipline_score = max(1, 5 - penalty)  # 5 is best (no cards/fouls), 1 worst
    except PlayerDefensiveStats.DoesNotExist:
        discipline_score = 5

    # --- Persist ---
    rating, _ = PerformanceRating.objects.get_or_create(player=player, match=match)
    rating.attacking = attacking_score
    rating.creativity = creativity_score
    rating.defending = defending_score
    rating.tactical = tactical_score
    rating.technical = technical_score
    # ensure PerformanceRating model has 'discipline' column (see migration note)
    rating.discipline = discipline_score
    rating.is_computed = True
    rating.save()
    return rating
