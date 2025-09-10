# perfomance_rating_app/services.py
from tagging_app.models import AttemptToGoal, PassEvent
from lineup_app.models import MatchLineup
from perfomance_rating_app.models import PerformanceRating

def compute_player_rating(player, match):
    # Attacking: Based on shots, goals
    attempts = AttemptToGoal.objects.filter(match=match, player=player)
    goals = attempts.filter(outcome='On Target Goal').count()
    shots = attempts.count()

    attacking_score = min(5, goals + shots // 3)

    # Creativity: Based on assists and passes
    assists = attempts.filter(assist_by=player).count()
    passes = PassEvent.objects.filter(match=match, from_player=player).count()

    creativity_score = min(5, assists + passes // 10)

    # Defending: Placeholder (can use GPS or defensive app later)
    defending_score = 3  # default or calculated from defensive_app

    # Tactical: Use minutes played as proxy for trust in match plan
    try:
        lineup = MatchLineup.objects.get(match=match, player=player)
        tactical_score = min(5, lineup.minutes_played // 20)  # e.g., 90 mins = 4–5
    except MatchLineup.DoesNotExist:
        tactical_score = 1

    # Technical: Pass success rate
    total_passes = PassEvent.objects.filter(match=match, from_player=player).count()
    successful_passes = PassEvent.objects.filter(match=match, from_player=player, is_successful=True).count()

    if total_passes > 0:
        pass_accuracy = successful_passes / total_passes
        technical_score = round(pass_accuracy * 5)
    else:
        technical_score = 2

    # Save or update rating
    rating, created = PerformanceRating.objects.get_or_create(player=player, match=match)
    rating.attacking = attacking_score
    rating.creativity = creativity_score
    rating.defending = defending_score
    rating.tactical = tactical_score
    rating.technical = technical_score
    rating.is_computed = True
    rating.save()

    return rating
