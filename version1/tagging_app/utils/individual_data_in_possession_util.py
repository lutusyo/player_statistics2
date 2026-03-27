from tagging_app.models import PassEvent, GoalkeeperDistributionEvent, AttemptToGoal
from lineup_app.models import MatchLineup  # to fetch players who appeared

def get_player_in_possession_data(match, player):
    """Return dict of possession stats for one player in one match."""

    # Passes
    passes_attempted = PassEvent.objects.filter(match=match, from_player=player).count()
    passes_completed = PassEvent.objects.filter(match=match, from_player=player, is_successful=True).count()
    pass_completion = round((passes_completed / passes_attempted) * 100, 2) if passes_attempted else 0

    # Line breaks (you can refine this definition later)
    line_breaks_attempted = PassEvent.objects.filter(match=match, from_player=player).exclude(to_player=None).count()
    line_breaks_completed = PassEvent.objects.filter(match=match, from_player=player, is_successful=True).exclude(to_player=None).count()
    line_break_completion = round((line_breaks_completed / line_breaks_attempted) * 100, 2) if line_breaks_attempted else 0

    # Goalkeeper distributions
    gk_dist_attempted = GoalkeeperDistributionEvent.objects.filter(match=match, goalkeeper=player).count()
    gk_dist_completed = GoalkeeperDistributionEvent.objects.filter(match=match, goalkeeper=player, is_complete=True).count()

    # Attempts at goal
    attempts = AttemptToGoal.objects.filter(match=match, player=player)
    attempts_count = attempts.count()
    goals = attempts.filter(outcome="On Target Goal").count()

    return {
        "player": player,
        "passes_attempted": passes_attempted,
        "passes_completed": passes_completed,
        "pass_completion": pass_completion,
        "line_breaks_attempted": line_breaks_attempted,
        "line_breaks_completed": line_breaks_completed,
        "line_break_completion": line_break_completion,
        "gk_dist_attempted": gk_dist_attempted,
        "gk_dist_completed": gk_dist_completed,
        "attempts": attempts_count,
        "goals": goals,
    }


def get_match_in_possession_data(match, team=None):
    """Return possession stats for all players in a match (optionally filter by team)."""
    players = MatchLineup.objects.filter(match=match)
    if team:
        players = players.filter(team=team)

    stats = []
    for lineup in players.select_related("player"):
        stats.append(get_player_in_possession_data(match, lineup.player))

    return stats
