from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from matches_app.models import Match
from tagging_app.models import AttemptToGoal, DeliveryTypeChoices, OutcomeChoices
from teams_app.models import Team
from lineup_app.models import MatchLineup

def setplays_dashboard(request, match_id, team_id):
    """
    View to analyze and display all set plays (corners, free kicks, penalties)
    for a given match and team.
    """
    match = get_object_or_404(Match, id=match_id)
    team = get_object_or_404(Team, id=team_id)

    # ✅ Get lineup players for context
    lineup = (
        MatchLineup.objects.filter(match=match, team=team)
        .select_related("player")
        .order_by("order", "player__name")
    )
    players = [entry.player for entry in lineup]

    # ✅ All our attempts for this team (not opponents)
    our_attempts = AttemptToGoal.objects.filter(match=match, team=team, is_opponent=False)

    # ✅ Filter by set play types explicitly
    corners = our_attempts.filter(delivery_type=DeliveryTypeChoices.CORNER)
    free_kicks = our_attempts.filter(delivery_type=DeliveryTypeChoices.FREE_KICK)  # using explicit choice
    penalties = our_attempts.filter(location_tag__iexact='Penalty Spot')

    # ✅ Combine for total setplays
    setplays = corners | free_kicks | penalties

    # ✅ Summary counts
    summary = {
        "total_corners": corners.count(),
        "total_free_kicks": free_kicks.count(),
        "total_penalties": penalties.count(),
        "total_setplays": setplays.count(),
        "goals_from_setplays": setplays.filter(outcome=OutcomeChoices.ON_TARGET_GOAL).count(),
        "on_target_from_setplays": setplays.filter(outcome__in=[
            OutcomeChoices.ON_TARGET_GOAL,
            OutcomeChoices.ON_TARGET_SAVED
        ]).count(),
        "blocked_setplays": setplays.filter(outcome=OutcomeChoices.BLOCKED).count(),
        "off_target_setplays": setplays.filter(outcome=OutcomeChoices.OFF_TARGET).count(),
    }

    # ✅ Player-wise set play contribution
    player_summary = (
        setplays.values("player__name", "delivery_type")
        .annotate(total=Count("id"))
        .order_by("player__name", "delivery_type")
    )

    context = {
        "match": match,
        "team": team,
        "players": players,
        "setplays": setplays,
        "corners": corners,
        "free_kicks": free_kicks,
        "penalties": penalties,
        "summary": summary,
        "player_summary": player_summary,
        "home_team": match.home_team,
        "away_team": match.away_team,
    }

    return render(request, "reports_app/match_report_templates/7_set_plays/set_plays.html", context)
