
def safe_rate(value, matches):
    return round(value / matches, 2) if matches else 0


def compare_metric(
    category,
    metric,
    label,
    current_value,
    previous_value,
    higher_is_better=True,
    threshold=0.1,
):
    change = round(current_value - previous_value, 2)

    if abs(change) < threshold:
        return {
            "category": category,
            "metric": metric,
            "status": "stable",
            "message": f"{label} remained relatively stable.",
            "current_value": current_value,
            "previous_value": previous_value,
            "change": change,
        }

    improved = (
        change > 0 if higher_is_better else change < 0
    )

    return {
        "category": category,
        "metric": metric,
        "status": "improved" if improved else "declined",
        "message": (
            f"{label} improved."
            if improved else f"{label} declined."
        ),
        "current_value": current_value,
        "previous_value": previous_value,
        "change": change,
    }


def generate_performance_insights(comparison):
    current = comparison["current"]
    previous = comparison["previous"]

    matches = current.get("played", 0)

    insights = []

    if matches == 0:
        return [{
            "category": "General",
            "metric": "played",
            "status": "no_data",
            "message": "No finished matches were recorded in this period.",
        }]

    current_metrics = {
        "points_per_match": safe_rate(
            current.get("points", 0), matches
        ),
        "goals_for_per_match": safe_rate(
            current.get("goals_for", 0), matches
        ),
        "goals_against_per_match": safe_rate(
            current.get("goals_against", 0), matches
        ),
        "shots_per_match": safe_rate(
            current.get("shots", 0), matches
        ),
    }

    if previous and previous.get("played", 0) > 0:
        previous_matches = previous["played"]

        previous_metrics = {
            "points_per_match": safe_rate(
                previous.get("points", 0), previous_matches
            ),
            "goals_for_per_match": safe_rate(
                previous.get("goals_for", 0), previous_matches
            ),
            "goals_against_per_match": safe_rate(
                previous.get("goals_against", 0), previous_matches
            ),
            "shots_per_match": safe_rate(
                previous.get("shots", 0), previous_matches
            ),
        }

        comparisons = [
            (
                "Results",
                "points_per_match",
                "Points per match",
                True,
                0.1,
            ),
            (
                "Attack",
                "goals_for_per_match",
                "Goals scored per match",
                True,
                0.1,
            ),
            (
                "Defence",
                "goals_against_per_match",
                "Goals conceded per match",
                False,
                0.1,
            ),
            (
                "Shooting",
                "shooting_accuracy",
                "Shooting accuracy",
                True,
                2,
            ),
            (
                "Passing",
                "pass_accuracy",
                "Pass accuracy",
                True,
                2,
            ),
        ]

        for category, metric, label, higher, threshold in comparisons:
            if metric in current_metrics:
                current_value = current_metrics[metric]
                previous_value = previous_metrics[metric]
            else:
                current_value = current.get(metric, 0)
                previous_value = previous.get(metric, 0)

            insights.append(
                compare_metric(
                    category,
                    metric,
                    label,
                    current_value,
                    previous_value,
                    higher_is_better=higher,
                    threshold=threshold,
                )
            )

        # Shot volume is descriptive, not automatically positive.
        shot_change = round(
            current_metrics["shots_per_match"]
            - previous_metrics["shots_per_match"],
            2,
        )

        insights.append({
            "category": "Shooting",
            "metric": "shots_per_match",
            "status": "increased" if shot_change > 0 else (
                "decreased" if shot_change < 0 else "stable"
            ),
            "message": (
                f"Shots per match increased by {shot_change}."
                if shot_change > 0 else
                f"Shots per match decreased by {abs(shot_change)}."
                if shot_change < 0 else
                "Shots per match remained stable."
            ),
            "current_value": current_metrics["shots_per_match"],
            "previous_value": previous_metrics["shots_per_match"],
            "change": shot_change,
        })

    else:
        insights.append({
            "category": "General",
            "metric": "comparison",
            "status": "no_previous_data",
            "message": (
                "No previous period is available for comparison. "
                "The current period will be used as the baseline."
            ),
        })

    # Current-period observations
    insights.append({
        "category": "Results",
        "metric": "points_per_match",
        "status": "observation",
        "message": (
            f"The team collected {current_metrics['points_per_match']} "
            "points per match."
        ),
    })

    insights.append({
        "category": "Attack",
        "metric": "goals_for_per_match",
        "status": "observation",
        "message": (
            f"The team scored {current_metrics['goals_for_per_match']} "
            "goals per match."
        ),
    })

    insights.append({
        "category": "Defence",
        "metric": "goals_against_per_match",
        "status": "observation",
        "message": (
            f"The team conceded "
            f"{current_metrics['goals_against_per_match']} goals per match."
        ),
    })

    return insights


def generate_all_performance_insights(comparisons):
    output = []

    for comparison in comparisons:
        output.append({
            "period_id": comparison["period_id"],
            "period_name": comparison["period_name"],
            "team_id": comparison["team_id"],
            "team_name": comparison["team_name"],
            "insights": generate_performance_insights(comparison),
        })

    return output
