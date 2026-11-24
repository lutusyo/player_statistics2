
def build_period_comparisons(analysis, results):
    """
    Compare each team's current period with the immediately
    preceding period, when that same team was selected.
    """

    periods = list(
        analysis.periods.all().order_by("order")
    )

    period_order = {
        period.id: index
        for index, period in enumerate(periods)
    }

    results_by_period_team = {
        (row["period_id"], row["team_id"]): row
        for row in results
    }

    metrics = [
        "played",
        "won",
        "drawn",
        "lost",
        "goals_for",
        "goals_against",
        "goal_difference",
        "points",
        "win_percentage",
        "shots",
        "shots_on_target",
        "shooting_accuracy",
        "passes_attempted",
        "passes_completed",
        "pass_accuracy",
        "players_used",
        "player_appearances",
        "total_player_minutes",
    ]

    percentage_metrics = {
        "win_percentage",
        "shooting_accuracy",
        "pass_accuracy",
    }

    comparison_rows = []

    for period_index, period in enumerate(periods):
        current_results = [
            row for row in results
            if row["period_id"] == period.id
        ]

        previous_period = (
            periods[period_index - 1]
            if period_index > 0 else None
        )

        for current in current_results:
            previous = None

            if previous_period:
                previous = results_by_period_team.get(
                    (previous_period.id, current["team_id"])
                )

            changes = {}

            for metric in metrics:
                current_value = current.get(metric, 0) or 0
                previous_value = (
                    previous.get(metric, 0) or 0
                    if previous else None
                )

                if previous_value is None:
                    changes[metric] = None
                else:
                    changes[metric] = round(
                        current_value - previous_value, 1
                    )

            comparison_rows.append({
                "period_id": period.id,
                "period_name": period.name,
                "team_id": current["team_id"],
                "team_name": current["team_name"],
                "previous_period_name": (
                    previous["period_name"] if previous else None
                ),
                "has_previous_comparison": previous is not None,
                "current": current,
                "previous": previous,
                "changes": changes,
                "percentage_metrics": list(percentage_metrics),
            })

    return comparison_rows
