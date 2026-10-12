from datetime import date, timedelta

from django.db.models import Sum
from django.shortcuts import render

from version1.teams_app.models import AgeGroup
from apps.individual_data.models.data_collection import (
    TrainingSession,
    PlayerParticipation,
    PlayerIntervention,
    PlayerInterventionCoachingPoint,
)


def weekly_report(request):
    age_groups = AgeGroup.objects.all().order_by("name")

    today = date.today()
    default_start = today - timedelta(days=today.weekday())
    default_end = default_start + timedelta(days=6)

    age_group_id = request.GET.get("age_group")
    week_start = request.GET.get("week_start", default_start.isoformat())
    week_end = request.GET.get("week_end", default_end.isoformat())

    # Validate the date inputs.
    try:
        week_start = date.fromisoformat(week_start)
        week_end = date.fromisoformat(week_end)

        if week_end < week_start:
            raise ValueError

        dates_valid = True
    except (ValueError, TypeError):
        week_start = default_start
        week_end = default_end
        dates_valid = False

    selected_age_group = age_groups.filter(pk=age_group_id).first()

    sessions = TrainingSession.objects.none()
    participations = PlayerParticipation.objects.none()
    interventions = PlayerIntervention.objects.none()
    coaching_selections = PlayerInterventionCoachingPoint.objects.none()

    if dates_valid and selected_age_group:
        sessions = (
            TrainingSession.objects.filter(
                age_group=selected_age_group,
                date__range=(week_start, week_end),
            )
            .select_related("age_group", "team", "coach")
            .prefetch_related(
                "session_topics__topic",
                "session_topics__objective",
                "player_participations__player",
                "player_participations__interventions__session_topic__topic",
                "player_participations__interventions__session_topic__objective",
                "player_participations__interventions__coaching_points__coaching_point",
            )
            .order_by("date")
        )

        participations = PlayerParticipation.objects.filter(
            session__in=sessions
        )

        interventions = PlayerIntervention.objects.filter(
            player_participation__session__in=sessions
        )

        coaching_selections = PlayerInterventionCoachingPoint.objects.filter(
            intervention__in=interventions
        )

    statistics = {
        "sessions": sessions.count(),
        "players": participations.values("player_id").distinct().count(),
        "interventions": interventions.count(),
        "coaching_points": coaching_selections.count(),
        "achieved": coaching_selections.filter(achieved=True).count(),
        "player_minutes": (
            participations.aggregate(total=Sum("minutes"))["total"] or 0
        ),
    }

    context = {
        "age_groups": age_groups,
        "selected_age_group": selected_age_group,
        "week_start": week_start,
        "week_end": week_end,
        "dates_valid": dates_valid,
        "sessions": sessions,
        "statistics": statistics,
    }

    return render(
        request,
        "individual_data/weekly_report.html",
        context,
    )