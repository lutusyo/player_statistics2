
from datetime import timedelta
from django.db.models import Count, Sum, Q
from django.shortcuts import render
from django.utils import timezone

from version1.teams_app.models import Team
from ..models.previous_models import (
    TrainingMinutes,
    PlayerTrainingMinutes,
    TrainingParticipationType,
)


def training_minutes_dashboard(request):
    today = timezone.localdate()

    # Default period: current month
    start_date = request.GET.get(
        "start_date",
        today.replace(day=1).isoformat()
    )
    end_date = request.GET.get("end_date", today.isoformat())
    team_id = request.GET.get("team", "")

    teams = Team.objects.filter(team_type="OUR_TEAM").select_related("age_group").order_by(
        "age_group__code", "name")

    sessions = TrainingMinutes.objects.filter(
        date__gte=start_date,
        date__lte=end_date,
        team__team_type="OUR_TEAM",
    ).select_related("team", "team__age_group")

    if team_id:
        sessions = sessions.filter(team_id=team_id)

    # Overall session count
    total_sessions = sessions.count()

    # Player-minutes, calculated from individual player records
    player_records = PlayerTrainingMinutes.objects.filter(
        training_session__in=sessions
    )

    total_player_minutes = (
        player_records.aggregate(total=Sum("minutes"))["total"] or 0
    )

    total_player_records = player_records.count()

    average_player_minutes = (
        round(total_player_minutes / total_player_records, 1)
        if total_player_records else 0
    )

    # Participation breakdown
    participation_breakdown = {
        item["participation_type"]: item["total"]
        for item in player_records.values(
            "participation_type"
        ).annotate(total=Count("id"))
    }

    participation_labels = dict(
        TrainingParticipationType.choices
    )

    participation_summary = [
        {
            "value": key,
            "label": participation_labels.get(key, key),
            "count": participation_breakdown.get(key, 0),
        }
        for key, label in TrainingParticipationType.choices
    ]

    # Team-by-team comparison
    team_summary = []

    selected_teams = teams
    if team_id:
        selected_teams = selected_teams.filter(id=team_id)

    for team in selected_teams:
        team_sessions = sessions.filter(team=team)

        session_count = team_sessions.count()

        team_player_minutes = (
            PlayerTrainingMinutes.objects.filter(
                training_session__in=team_sessions
            ).aggregate(total=Sum("minutes"))["total"] or 0
        )

        team_record_count = PlayerTrainingMinutes.objects.filter(
            training_session__in=team_sessions
        ).count()

        team_summary.append({
            "team": team,
            "sessions": session_count,
            "player_minutes": team_player_minutes,
            "average_player_minutes_per_session": (
                round(team_player_minutes / session_count, 1)
                if session_count else 0
            ),
            "average_minutes_per_player_record": (
                round(team_player_minutes / team_record_count, 1)
                if team_record_count else 0
            ),
        })

    context = {
        "teams": teams,
        "selected_team_id": team_id,
        "start_date": start_date,
        "end_date": end_date,
        "total_sessions": total_sessions,
        "total_player_minutes": total_player_minutes,
        "total_player_records": total_player_records,
        "average_player_minutes": average_player_minutes,
        "team_summary": team_summary,
        "participation_summary": participation_summary,
    }

    return render(request, "training_minutes/training_minutes_dashboard.html", context,)
