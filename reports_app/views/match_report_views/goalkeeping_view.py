# reports_app/views/match_report_views/goalkeeping_view.py
from django.shortcuts import render, get_object_or_404
from matches_app.models import Match
from teams_app.models import Team
from players_app.models import Player
from tagging_app.models import AttemptToGoal, PassEvent, OutcomeChoices

def goalkeeping_view(request, match_id, our_team_id, return_context=False):
    match = get_object_or_404(Match, id=match_id)
    our_team = get_object_or_404(Team, id=our_team_id)

    # Opponent team attempts
    opponents_attempts = AttemptToGoal.objects.filter(match=match, is_opponent=True)
    our_attempts = AttemptToGoal.objects.filter(match=match, is_opponent=False)

    # Goalkeeping metrics
    total_attempts_faced = opponents_attempts.count()
    our_goalkeeper_on_target_faced = opponents_attempts.filter(
        outcome__in=[OutcomeChoices.ON_TARGET_SAVED, OutcomeChoices.ON_TARGET_GOAL]
    ).count()
    our_goalkeeper_saves_made = opponents_attempts.filter(outcome=OutcomeChoices.ON_TARGET_SAVED).count()
    our_goalkeeper_goals_conceded = (
        opponents_attempts.filter(outcome=OutcomeChoices.ON_TARGET_GOAL).count() +
        our_attempts.filter(outcome=OutcomeChoices.OWN_GOAL).count()
    )
    our_goalkeeper_save_percentage = round(
        (our_goalkeeper_saves_made / our_goalkeeper_on_target_faced * 100), 2
    ) if our_goalkeeper_on_target_faced > 0 else 0
    clean_sheet = our_goalkeeper_goals_conceded == 0

    # Goalkeeping distribution
    our_goalkeeper = Player.objects.filter(team=our_team, position__icontains='goal').first()
    total_passes = 0
    successful_passes = 0
    our_goalkeeper_total_involvements = 0
    our_goalkeeper_long_passes = 0
    our_goalkeeper_successful_long_passes = 0
    our_goalkeeper_long_passes_ratio = 0

    if our_goalkeeper:
        passes = PassEvent.objects.filter(match=match, from_player=our_goalkeeper)
        total_passes = passes.count()
        successful_passes = passes.filter(is_successful=True).count()

        # Count all involvements (pass made + pass received)
        our_goalkeeper_total_involvements = (
            PassEvent.objects.filter(match=match, from_player=our_goalkeeper).count() +
            PassEvent.objects.filter(match=match, to_player=our_goalkeeper).count()
        )

        # Long passes → passes to forwards or wingers
        long_pass_recipients = Player.objects.filter(team=our_team, position__iregex=r"(forward|wing)")
        long_pass_qs = passes.filter(to_player__in=long_pass_recipients)
        our_goalkeeper_long_passes = long_pass_qs.count()
        our_goalkeeper_successful_long_passes = long_pass_qs.filter(is_successful=True).count()

        if our_goalkeeper_long_passes > 0:
            our_goalkeeper_long_passes_ratio = round(
                (our_goalkeeper_successful_long_passes / our_goalkeeper_long_passes) * 100, 2
            )

    our_goalkeeper_pass_accuracy = round(
        (successful_passes / total_passes * 100), 2
    ) if total_passes > 0 else 0

    context = {
        "match": match,
        "our_team": our_team,
        "goalkeeper": our_goalkeeper,
        "total_attempts_faced": total_attempts_faced,
        "goalkeeper_on_target_faced": our_goalkeeper_on_target_faced,
        "goalkeeper_saves_made": our_goalkeeper_saves_made,
        "our_goalkeeper_goals_conceded": our_goalkeeper_goals_conceded,
        "our_goalkeeper_save_percentage": our_goalkeeper_save_percentage,
        "clean_sheet": clean_sheet,
        "total_passes": total_passes,
        "successful_passes": successful_passes,
        "our_goalkeeper_pass_accuracy": our_goalkeeper_pass_accuracy,
        "our_goalkeeper_total_involvements": our_goalkeeper_total_involvements,
        "our_goalkeeper_long_passes": our_goalkeeper_long_passes,
        "our_goalkeeper_successful_long_passes": our_goalkeeper_successful_long_passes,
        "our_goalkeeper_long_passes_ratio": our_goalkeeper_long_passes_ratio,
    }

    if return_context:
        return context


    return render(request, 'reports_app/match_report_templates/6_goalkeeping/goalkeeping.html', context)
