from django.shortcuts import get_object_or_404
from tagging_app.models import AttemptToGoal, PassEvent, GoalkeeperDistributionEvent
from matches_app.models import Match
from teams_app.models import Team
from players_app.models import Player
from collections import defaultdict


def get_match_full_context(match_id, our_team_id):
    """
    Extract all possible stats for our team and opponent:
    - Attempts to Goal
    - Passes
    - Goalkeeper distributions
    """
    match = get_object_or_404(Match, id=match_id)
    our_team = get_object_or_404(Team, id=our_team_id)
    opponent_team = match.home_team if match.away_team == our_team else match.away_team

    # ======================
    # 1. ATTEMPTS TO GOAL
    # ======================
    our_attempts = AttemptToGoal.objects.filter(match=match, team=our_team, is_opponent=False)
    opponent_attempts = AttemptToGoal.objects.filter(match=match, team=opponent_team, is_opponent=True)

    def process_attempts(qs, team):
        own_goals_for_team = AttemptToGoal.objects.filter(match=match, is_own_goal=True, own_goal_for=team)

        return {
            "total_goals": (
                qs.filter(outcome="On Target Goal", is_own_goal=False).count()
                + own_goals_for_team.count()
            ),
            "total_assists": qs.filter(assist_by__isnull=False, is_own_goal=False).count(),
            "off_target": qs.filter(outcome="Off Target").count(),
            "on_target_goal": qs.filter(outcome="On Target Goal", is_own_goal=False).count(),
            "on_target_saved": qs.filter(outcome="On Target Saved").count(),
            "blocked": qs.filter(outcome="Blocked").count(),
            "big_chance_missed": qs.filter(outcome="Player Error").count(),
            "corners": qs.filter(delivery_type="Corner").count(),
            "crosses": qs.filter(delivery_type="Cross").count(),
            "times": list(qs.values_list("minute", "second")),
        }

    # Aggregated stats
    our_attempt_stats = process_attempts(our_attempts, our_team)
    opponent_attempt_stats = process_attempts(opponent_attempts, opponent_team)

    # Per-player stats (our team only)
    per_player_attempts = defaultdict(dict)
    for player in Player.objects.filter(team=our_team):
        qs = our_attempts.filter(player=player)
        if qs.exists():
            per_player_attempts[player.id] = process_attempts(qs, our_team)

    # ======================
    # 2. PASS EVENTS
    # ======================
    our_passes = PassEvent.objects.filter(match=match, from_team=our_team)
    opponent_passes = PassEvent.objects.filter(match=match, from_team=opponent_team)

    def process_passes(qs):
        return {
            "total_passes": qs.count(),
            "successful": qs.filter(is_successful=True).count(),
            "failed": qs.filter(is_successful=False).count(),
            "possession_regained": qs.filter(is_possession_regained=True).count(),
            "times": list(qs.values_list("minute", "second")),
        }

    our_pass_stats = process_passes(our_passes)
    opponent_pass_stats = process_passes(opponent_passes)

    # Per-player passes (our team only)
    per_player_passes = defaultdict(dict)
    for player in Player.objects.filter(team=our_team):
        qs = our_passes.filter(from_player=player)
        if qs.exists():
            per_player_passes[player.id] = process_passes(qs)

    # Passing network (our team only)
    passing_network = defaultdict(lambda: defaultdict(int))
    for p in our_passes:
        if p.from_player and p.to_player:
            passing_network[p.from_player.id][p.to_player.id] += 1

    # ======================
    # 3. GOALKEEPER DISTRIBUTIONS
    # ======================
    our_gk_dists = GoalkeeperDistributionEvent.objects.filter(match=match, team=our_team)
    opponent_gk_dists = GoalkeeperDistributionEvent.objects.filter(match=match, team=opponent_team)

    def process_gk(qs):
        return {
            "total": qs.count(),
            "complete": qs.filter(is_complete=True).count(),
            "incomplete": qs.filter(is_complete=False).count(),
            "conceded": qs.filter(is_goal_conceded=True).count(),
            "times": list(qs.values_list("minute", "second")),
        }

    our_gk_stats = process_gk(our_gk_dists)
    opponent_gk_stats = process_gk(opponent_gk_dists)

    # Per goalkeeper (our team)
    per_gk_stats = defaultdict(dict)
    for gk in Player.objects.filter(team=our_team, gk_distributions__match=match).distinct():
        qs = our_gk_dists.filter(goalkeeper=gk)
        per_gk_stats[gk.id] = process_gk(qs)

    # ======================
    # FINAL CONTEXT
    # ======================
    return {
        "match": match,
        "our_team": {
            "obj": our_team,
            "aggregate": {
                "attempts": our_attempt_stats,
                "passes": our_pass_stats,
                "goalkeeper": our_gk_stats,
            },
            "per_player": {
                "attempts": per_player_attempts,
                "passes": per_player_passes,
                "goalkeeper": per_gk_stats,
            },
            "passing_network": passing_network,
        },
        "opponent_team": {
            "obj": opponent_team,
            "aggregate": {
                "attempts": opponent_attempt_stats,
                "passes": opponent_pass_stats,
                "goalkeeper": opponent_gk_stats,
            }
        },
    }
