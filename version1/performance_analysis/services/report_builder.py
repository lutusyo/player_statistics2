
from .match_analysis import generate_team_match_analysis
from .period_comparison import build_period_comparisons
from .performance_insights import generate_all_performance_insights

from version1.performance_analysis.services.player_analysis import ( get_player_stats,)
from version1.performance_analysis.services.match_analysis import (get_period_teams, get_finished_matches,)

from version1.teams_app.models import Team
from version1.performance_analysis.services.technical_analysis import build_technical_analysis
from version1.performance_analysis.models import AnalysisPeriodSquadPhoto



def build_player_analysis(analysis):
    player_analysis = []
    

    for period in analysis.periods.order_by("order"):
        team_ids = get_period_teams(analysis, period)

        teams = Team.objects.filter(
            id__in=team_ids,
            team_type="OUR_TEAM",
        )

        period_teams = []

        for team in teams:
            matches = get_finished_matches(period, [team.id])
            match_ids = [match.id for match in matches]

            stats = get_player_stats(team, match_ids)
            period_teams.append(stats)

        player_analysis.append({
            "period_id": period.id,
            "period_name": period.name,
            "teams": period_teams,
        })

    return player_analysis


def build_analysis_report(analysis):
    # Generate statistics
    results = generate_team_match_analysis(analysis)
    player_analysis = build_player_analysis(analysis)
    technical_analysis = build_technical_analysis(analysis)

    # Compare periods
    comparisons = build_period_comparisons(analysis, results,)

    # Generate football insights
    insights = generate_all_performance_insights(comparisons,)

    periods = list(
        analysis.periods.all().order_by("order")
    )

    period_data = [
        {
            "id": period.id,
            "name": period.name,
            "start_date": period.start_date.isoformat(),
            "end_date": period.end_date.isoformat(),
        }
        for period in periods
    ]





    # Prepare selected squad photos for each reporting period
    squad_photos = []

    photo_selections = (
        AnalysisPeriodSquadPhoto.objects
        .filter(period__analysis=analysis)
        .select_related(
            "period",
            "team",
            "squad_photo",
        )
        .order_by("period__order", "team__name")
    )

    for selection in photo_selections:
        photo = selection.squad_photo

        squad_photos.append({
            "period_id": selection.period_id,
            "period_name": selection.period.name,
            "team_id": selection.team_id,
            "team_name": selection.team.name,
            "photo_id": photo.id,
            "photo_path": photo.photo.name if photo.photo else "",
            "photo_date": photo.photo_date.isoformat(),
            "label": photo.label,
            "notes": photo.notes,
        })





    # Get unique teams
    teams = {}

    for row in results:
        teams[row["team_id"]] = {
            "id": row["team_id"],
            "name": row["team_name"],
            "age_group": row["age_group"],
        }

    # Prepare chart data for each team
    team_charts = []

    for team_id, team in teams.items():
        team_results = {
            row["period_id"]: row
            for row in results
            if row["team_id"] == team_id
        }

        chart = {
            "team_id": team_id,
            "team_name": team["name"],
            "age_group": team["age_group"],
            "labels": [],
            "points": [],
            "goals_for": [],
            "goals_against": [],
            "win_percentage": [],
            "shots": [],
            "shooting_accuracy": [],
            "pass_accuracy": [],
        }

        for period in periods:
            row = team_results.get(period.id)

            chart["labels"].append(period.name)

            for metric in [
                "points",
                "goals_for",
                "goals_against",
                "win_percentage",
                "shots",
                "shooting_accuracy",
                "pass_accuracy",
            ]:
                chart[metric].append(
                    row.get(metric, 0) if row else None
                )

        team_charts.append(chart)

    return {
        "analysis": {
            "id": analysis.id,
            "name": analysis.name,
            "description": analysis.description,
            "analysis_type": analysis.analysis_type,
            "comparison_mode": analysis.comparison_mode,
        },
        "periods": period_data,
        "teams": list(teams.values()),
        "results": results,
        "comparisons": comparisons,
        "insights": insights,
        "team_charts": team_charts,
        "player_analysis": player_analysis,
        "technical_analysis": technical_analysis,
        "squad_photos": squad_photos,
    }
