# reports_app/views/match_report_views/goalkeeping_view.py
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from matches_app.models import Match
from teams_app.models import Team
from players_app.models import Player
from tagging_app.models import AttemptToGoal, PassEvent, OutcomeChoices

def goalkeeping_view(request, match_id, our_team_id, return_context=False):
    match = get_object_or_404(Match, id=match_id)
    our_team = get_object_or_404(Team, id=our_team_id)

    # -----------------------------
    # 1️⃣ Opponent attempts
    # -----------------------------
    opponents_attempts = AttemptToGoal.objects.filter(match=match, is_opponent=True)
    our_attempts = AttemptToGoal.objects.filter(match=match, is_opponent=False)

    total_attempts_faced = opponents_attempts.count()
    on_target_faced = opponents_attempts.filter(
        outcome__in=[OutcomeChoices.ON_TARGET_SAVED, OutcomeChoices.ON_TARGET_GOAL]
    ).count()
    saves_made = opponents_attempts.filter(outcome=OutcomeChoices.ON_TARGET_SAVED).count()
    goals_conceded = (
        opponents_attempts.filter(outcome=OutcomeChoices.ON_TARGET_GOAL).count() +
        our_attempts.filter(outcome=OutcomeChoices.OWN_GOAL).count()
    )
    save_percentage = round((saves_made / on_target_faced * 100), 2) if on_target_faced > 0 else 0
    clean_sheet = goals_conceded == 0

    # -----------------------------
    # 2️⃣ Get goalkeeper reliably
    # -----------------------------
    goalkeeper = Player.objects.filter(
        team=our_team
    ).filter(
        Q(position='Goalkeeper') | Q(specific_position='GK')
    ).first()

    # Initialize distribution metrics
    total_passes = 0
    successful_passes = 0
    total_involvements = 0
    long_passes = 0
    successful_long_passes = 0
    long_pass_ratio = 0
    pass_accuracy = 0

    if goalkeeper:
        passes = PassEvent.objects.filter(match=match, from_player=goalkeeper)
        total_passes = passes.count()
        successful_passes = passes.filter(is_successful=True).count()

        # Total involvements (passes made + received)
        total_involvements = passes.count() + PassEvent.objects.filter(match=match, to_player=goalkeeper).count()

        # Long passes → passes to forwards or wingers
        long_pass_recipients = Player.objects.filter(
            team=our_team, 
            position__iregex=r'(forward|wing)'
        )
        long_pass_qs = passes.filter(to_player__in=long_pass_recipients)
        long_passes = long_pass_qs.count()
        successful_long_passes = long_pass_qs.filter(is_successful=True).count()
        if long_passes > 0:
            long_pass_ratio = round((successful_long_passes / long_passes) * 100, 2)

        # Pass accuracy
        if total_passes > 0:
            pass_accuracy = round((successful_passes / total_passes) * 100, 2)

    # -----------------------------
    # 3️⃣ Prepare context
    # -----------------------------
    context = {
        "match": match,
        "our_team": our_team,
        "goalkeeper": goalkeeper,
        "total_attempts_faced": total_attempts_faced,
        "goalkeeper_on_target_faced": on_target_faced,
        "goalkeeper_saves_made": saves_made,
        "our_goalkeeper_goals_conceded": goals_conceded,
        "our_goalkeeper_save_percentage": save_percentage,
        "clean_sheet": clean_sheet,
        "total_passes": total_passes,
        "successful_passes": successful_passes,
        "our_goalkeeper_pass_accuracy": pass_accuracy,
        "our_goalkeeper_total_involvements": total_involvements,
        "our_goalkeeper_long_passes": long_passes,
        "our_goalkeeper_successful_long_passes": successful_long_passes,
        "our_goalkeeper_long_passes_ratio": long_pass_ratio,
    }

    if return_context:
        return context

    return render(
        request, 
        'reports_app/match_report_templates/6_goalkeeping/goalkeeping.html', 
        context
    )
