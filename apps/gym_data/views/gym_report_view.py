from collections import defaultdict
from decimal import Decimal

from django.shortcuts import get_object_or_404, render

from ..forms import GymReportFilterForm
from ..models import (
    GymSession,
    GymType,
    ExerciseCategory,
    Exercise,
)

from ..models import GymSession

from version1.teams_app.models import Team
from version1.players_app.models import Player


from ..report_utils import (
    get_report_queryset,
    apply_report_filters,
    add_volume,
)


def gym_report(request):
    """
    All Teams Gym Report.
    """

    form = GymReportFilterForm(request.GET or None)

    queryset = get_report_queryset()

    queryset = apply_report_filters(
        queryset,
        form,
    )

    queryset = add_volume(queryset)

    sessions = (
        GymSession.objects
        .filter(
            id__in=queryset.values(
                "gym_group__gym_session_id"
            )
        )
        .distinct()
    )

    teams = (
        Team.objects
        .filter(
            id__in=queryset.values(
                "gym_group__gym_session__team_id"
            )
        )
        .distinct()
    )

    players = set()

    for item in queryset:
        for player in item.gym_group.players.all():
            players.add(player.id)

    total_volume = sum(
        (item.volume or Decimal("0"))
        for item in queryset
    )

    total_exercises = queryset.count()

    category_data = defaultdict(Decimal)

    for item in queryset:
        category_data[
            item.exercise.category.name
        ] += item.volume or Decimal("0")

    team_data = defaultdict(Decimal)

    for item in queryset:
        team_data[
            item.gym_group.gym_session.team.name
        ] += item.volume or Decimal("0")

    context = {
        "form": form,
        "records": queryset,
        "sessions": sessions,
        "teams": teams,
        "player_count": len(players),
        "total_volume": total_volume,
        "total_exercises": total_exercises,
        "category_data": dict(category_data),
        "team_data": dict(team_data),
        "report_title": "All Teams Gym Report",
        "report_subtitle": "Gym training overview across teams",
    }

    return render(
        request,
        "gym_data/reports/all_teams.html",
        context,
    )


def gym_team_report(request, team_id):

    team = get_object_or_404(
        Team,
        id=team_id,
    )

    form = GymReportFilterForm(
        request.GET or None
    )

    queryset = get_report_queryset()

    queryset = queryset.filter(
        gym_group__gym_session__team=team
    )

    queryset = apply_report_filters(
        queryset,
        form,
    )

    queryset = add_volume(queryset)

    players = set()

    for item in queryset:
        for player in item.gym_group.players.all():
            players.add(player.id)

    total_volume = sum(
        (item.volume or Decimal("0"))
        for item in queryset
    )

    category_data = defaultdict(Decimal)
    date_data = defaultdict(Decimal)

    for item in queryset:

        category_data[
            item.exercise.category.name
        ] += item.volume or Decimal("0")

        date_data[
            item.gym_group.gym_session.date.strftime(
                "%Y-%m-%d"
            )
        ] += item.volume or Decimal("0")

    context = {
        "form": form,
        "records": queryset,
        "team": team,
        "player_count": len(players),
        "total_volume": total_volume,
        "total_exercises": queryset.count(),
        "category_data": dict(category_data),
        "date_data": dict(date_data),
        "report_title": f"{team.name} Gym Report",
        "report_subtitle": "Team gym training analysis",
    }

    return render(
        request,
        "gym_data/reports/team_report.html",
        context,
    )


def gym_player_report(request, player_id):

    player = get_object_or_404(
        Player,
        id=player_id,
    )

    form = GymReportFilterForm(
        request.GET or None
    )

    queryset = get_report_queryset()

    queryset = queryset.filter(
        gym_group__players=player
    )

    queryset = apply_report_filters(
        queryset,
        form,
    )

    queryset = add_volume(queryset)

    total_volume = sum(
        (item.volume or Decimal("0"))
        for item in queryset
    )

    category_data = defaultdict(Decimal)
    date_data = defaultdict(Decimal)

    for item in queryset:

        category_data[
            item.exercise.category.name
        ] += item.volume or Decimal("0")

        date_data[
            item.gym_group.gym_session.date.strftime(
                "%Y-%m-%d"
            )
        ] += item.volume or Decimal("0")

    context = {
        "form": form,
        "records": queryset,
        "player": player,
        "total_volume": total_volume,
        "total_exercises": queryset.count(),
        "category_data": dict(category_data),
        "date_data": dict(date_data),
        "report_title": f"{player.full_name} - Gym Report",
        "report_subtitle": "Player gym training analysis",
    }

    return render(
        request,
        "gym_data/reports/player_report.html",
        context,
    )