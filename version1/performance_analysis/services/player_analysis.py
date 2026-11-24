
from collections import defaultdict

from version1.lineup_app.models import MatchLineup
from version1.tagging_app.models import AttemptToGoal


def empty_player_stats(player_id, player_name):
    return {
        "player_id": player_id,
        "player_name": player_name,
        "appearances": 0,
        "starts": 0,
        "substitute_appearances": 0,
        "minutes": 0,
        "goals": 0,
        "assists": 0,
        "pre_assists": 0,
        "shots": 0,
        "shots_on_target": 0,
        "missing_entry_time": 0,
        "invalid_time_intervals": 0,
    }


def get_player_stats(team, match_ids):
    players = {}

    def get_player(player):
        if not player:
            return None

        if player.id not in players:
            players[player.id] = empty_player_stats(
                player.id,
                player.full_name,
            )

        return players[player.id]

    # 1. APPEARANCES AND MINUTES
    lineups = (
        MatchLineup.objects
        .filter(team=team, match_id__in=match_ids)
        .select_related("player")
    )

    for lineup in lineups:
        stats = get_player(lineup.player)

        if not stats:
            continue

        if lineup.is_unused_sub:
            continue

        if lineup.time_in is None:
            stats["missing_entry_time"] += 1
            continue

        final_minute = 90
        end_minute = (
            lineup.time_out
            if lineup.time_out is not None
            else final_minute
        )

        if end_minute < lineup.time_in:
            stats["invalid_time_intervals"] += 1
            continue

        minutes = end_minute - lineup.time_in

        stats["appearances"] += 1
        stats["minutes"] += minutes

        if lineup.is_starting:
            stats["starts"] += 1
        else:
            stats["substitute_appearances"] += 1

    # 2. SHOOTING AND ATTACKING CONTRIBUTIONS
    attempts = (
        AttemptToGoal.objects
        .filter(
            team=team,
            match_id__in=match_ids,
            is_opponent=False,
        )
        .exclude(outcome="Own Goal")
        .select_related(
            "player",
            "assist_by",
            "pre_assist_by",
        )
    )

    for attempt in attempts:
        player = get_player(attempt.player)

        if player:
            player["shots"] += 1

            if attempt.outcome in [
                "On Target Saved",
                "On Target Goal",
            ]:
                player["shots_on_target"] += 1

            if (
                attempt.outcome == "On Target Goal"
                and not attempt.is_own_goal
            ):
                player["goals"] += 1

        # Assists and pre-assists are attributed to the
        # players recorded on the goal event.
        if (
            attempt.outcome == "On Target Goal"
            and not attempt.is_own_goal
        ):
            assister = get_player(attempt.assist_by)
            pre_assister = get_player(attempt.pre_assist_by)

            if assister:
                assister["assists"] += 1

            if pre_assister:
                pre_assister["pre_assists"] += 1

    # 3. CALCULATE ADDITIONAL METRICS
    player_details = []

    for stats in players.values():
        stats["average_minutes_per_appearance"] = (
            round(stats["minutes"] / stats["appearances"], 1)
            if stats["appearances"] else 0
        )

        stats["goal_contributions"] = (
            stats["goals"]
            + stats["assists"]
            + stats["pre_assists"]
        )

        stats["goals_per_appearance"] = (
            round(stats["goals"] / stats["appearances"], 2)
            if stats["appearances"] else 0
        )

        player_details.append(stats)

    player_details.sort(
        key=lambda player: (
            player["goal_contributions"],
            player["goals"],
            player["minutes"],
        ),
        reverse=True,
    )

    return {
        "team_id": team.id,
        "team_name": team.name,
        "players_used": sum(
            1 for player in player_details
            if player["appearances"] > 0
        ),
        "total_appearances": sum(
            player["appearances"] for player in player_details
        ),
        "total_player_minutes": sum(
            player["minutes"] for player in player_details
        ),
        "players": player_details,
    }
