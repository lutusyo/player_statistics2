# Import aggregation and query utilities from Django ORM
from django.db.models import Count, Q
# Import the render shortcut to render templates
from django.shortcuts import render, get_object_or_404
from tagging_app.models import AttemptToGoal, DeliveryTypeChoices, OutcomeChoices
from matches_app.models import Match



def attempt_summary_view(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    our_attempts = AttemptToGoal.objects.filter(match=match, is_opponent=False)   # our team attempts
    
    # Filter by categories
    our_shots_on_target = our_attempts.filter(outcome__in=[OutcomeChoices.ON_TARGET_GOAL, OutcomeChoices.ON_TARGET_SAVED])
    our_shots_off_target = our_attempts.filter(outcome=OutcomeChoices.OFF_TARGET)
    our_blocked_shots = our_attempts.filter(outcome=OutcomeChoices.BLOCKED)
    our_player_errors = our_attempts.filter(outcome=OutcomeChoices.PLAYER_ERROR)

    our_corners = our_attempts.filter(delivery_type=DeliveryTypeChoices.CORNER)
    our_crosses = our_attempts.filter(delivery_type=DeliveryTypeChoices.CROSS)
    our_effective_loose_ball = our_attempts.filter(delivery_type=DeliveryTypeChoices.LOOSE_BALL)
    our_effective_pass = our_attempts.filter(delivery_type=DeliveryTypeChoices.PASS)

        
   # opponent_attempts = AttemptToGoal.objects.filter(match=match, is_opponent=True)     # opponents team attempts
    # Filter by categories
    #opponent_shots_on_target = opponent_attempts.filter(outcome__in=[OutcomeChoices.ON_TARGET_GOAL, OutcomeChoices.ON_TARGET_SAVED])
    #opponent_shots_off_target = opponent_attempts.filter(outcome=OutcomeChoices.OFF_TARGET)
    #opponent_blocked_shots = opponent_attempts.filter(outcome=OutcomeChoices.BLOCKED)
    #opponent_player_errors = opponent_attempts.filter(outcome=OutcomeChoices.PLAYER_ERROR)

    #opponent_corners = opponent_attempts.filter(delivery_type=DeliveryTypeChoices.CORNER)
    #opponent_crosses = opponent_attempts.filter(delivery_type=DeliveryTypeChoices.CROSS)

    context = {
        "match": match,
        "our_shots_on_target": our_shots_on_target,
        "our_shots_off_target": our_shots_off_target,
        "our_blocked_shots": our_blocked_shots,
        "our_player_errors": our_player_errors,

        "our_corners": our_corners,
        "our_crosses": our_crosses,
        "our_effective_loose_ball": our_effective_loose_ball,
        "our_effective_pass": our_effective_pass,
    }

    return render(request, "tagging_app/output/attempt_summary.html", context)