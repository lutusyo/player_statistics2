
from version1.lineup_app.models import MatchLineup


def calculate_team_player_minutes(team, match_ids):
    lineups = (
        MatchLineup.objects
        .filter(team=team, match_id__in=match_ids)
        .select_related("player")
    )

    stats = {
        "players_used": 0,
        "player_appearances": 0,
        "starting_appearances": 0,
        "substitute_appearances": 0,
        "unused_substitutes": 0,
        "total_player_minutes": 0,
        "average_minutes_per_appearance": 0,
        "missing_entry_time": 0,
        "invalid_time_intervals": 0,
        "player_details": [],
    }

    player_stats = {}

    for lineup in lineups:
        if not lineup.player:
            continue

        if lineup.is_unused_sub:
            stats["unused_substitutes"] += 1
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

        stats["player_appearances"] += 1
        stats["total_player_minutes"] += minutes

        if lineup.is_starting:
            stats["starting_appearances"] += 1
        else:
            stats["substitute_appearances"] += 1

        player_id = lineup.player_id

        if player_id not in player_stats:
            player_stats[player_id] = {
                "player_id": player_id,
                "player_name": lineup.player.full_name,
                "appearances": 0,
                "minutes": 0,
            }

        player_stats[player_id]["appearances"] += 1
        player_stats[player_id]["minutes"] += minutes

    stats["players_used"] = len(player_stats)

    if stats["player_appearances"]:
        stats["average_minutes_per_appearance"] = round(
            stats["total_player_minutes"] /
            stats["player_appearances"], 1
        )

    stats["player_details"] = sorted(
        player_stats.values(),
        key=lambda player: player["minutes"],
        reverse=True,
    )

    return stats
