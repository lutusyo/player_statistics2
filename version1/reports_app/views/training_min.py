from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from version1.players_app.models import Player
from version1.teams_app.models import Team
from ..models.previous_models import (TrainingMinutes, PlayerTrainingMinutes,
    TrainingSessionType, TrainingParticipationType,
)


def training_minutes_entry(request):
    teams = Team.objects.filter(team_type="OUR_TEAM").select_related("age_group").order_by(
        "age_group__code", "name"
    )

    other_teams = teams

    national_teams = Team.objects.filter(team_category="NATIONAL").select_related(
        "age_group"
    ).order_by("age_group__code", "name")

    selected_team = None
    players = []
    training_session = None

    if request.method == "GET":
        team_id = request.GET.get("team")
        date = request.GET.get("date")
        session_type = request.GET.get("session")

        if team_id:
            selected_team = get_object_or_404(
                Team.objects.select_related("age_group"),
                id=team_id,
                team_type="OUR_TEAM",
            )
            players = list(
                Player.objects.filter(team=selected_team, is_active=True).order_by(
                    "name", "second_name", "surname")
            )

            if date and session_type:
                training_session = TrainingMinutes.objects.filter(
                    team=selected_team, date=date, session=session_type
                ).first()

                if training_session:
                    records = PlayerTrainingMinutes.objects.filter(
                        training_session=training_session
                    ).select_related("trained_with_team")
                    record_map = {r.player_id: r for r in records}

                    for player in players:
                        player.training_record = record_map.get(player.id)

    elif request.method == "POST":
        team_id = request.POST.get("team")
        date = request.POST.get("date")
        session_type = request.POST.get("session")

        selected_team = get_object_or_404(
            Team.objects.select_related("age_group"),
            id=team_id,
            team_type="OUR_TEAM",
        )

        training_session, _ = TrainingMinutes.objects.get_or_create(
            team=selected_team,
            date=date,
            session=session_type,
            defaults={"total_minutes": 0},
        )

        players = Player.objects.filter(team=selected_team, is_active=True).order_by(
            "name", "second_name", "surname")

        total_minutes = 0

        for player in players:
            try:
                minutes = max(int(request.POST.get(f"minutes_{player.id}", 0) or 0), 0)
            except (TypeError, ValueError):
                minutes = 0

            participation_type = request.POST.get(
                f"participation_{player.id}",
                TrainingParticipationType.REGULAR,
            )
            other_team_id = request.POST.get(f"trained_with_team_{player.id}")
            national_team_id = request.POST.get(f"national_team_{player.id}")

            trained_with_team = None

            if participation_type == TrainingParticipationType.REGULAR:
                trained_with_team = selected_team
            elif participation_type == TrainingParticipationType.OTHER_TEAM and other_team_id:
                trained_with_team = Team.objects.filter(
                    id=other_team_id, team_type="OUR_TEAM"
                ).first()
            elif (
                participation_type == TrainingParticipationType.NATIONAL_TEAM
                and national_team_id
            ):
                trained_with_team = Team.objects.filter(
                    id=national_team_id, team_category="NATIONAL"
                ).first()

            if participation_type in (
                TrainingParticipationType.INJURED,
                TrainingParticipationType.ABSENT,
            ):
                minutes = 0

            PlayerTrainingMinutes.objects.update_or_create(
                training_session=training_session,
                player=player,
                defaults={
                    "minutes": minutes,
                    "participation_type": participation_type,
                    "trained_with_team": trained_with_team,
                },
            )
            total_minutes += minutes

        training_session.total_minutes = total_minutes
        training_session.save(update_fields=["total_minutes"])

        messages.success(request, "Training minutes saved successfully.")
        return redirect("reports_app:training_minutes_entry")

    context = {
        "teams": teams,
        "other_teams": other_teams,
        "national_teams": national_teams,
        "selected_team": selected_team,
        "players": players,
        "training_session": training_session,
        "session_types": TrainingSessionType.choices,
        "participation_types": TrainingParticipationType.choices,
    }
    return render(request, "training_minutes/training_minutes_entry.html", context)
