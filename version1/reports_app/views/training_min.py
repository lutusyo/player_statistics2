from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from version1.players_app.models import Player
from version1.teams_app.models import Team

from ..models.previous_models import (
    TrainingMinutes,
    PlayerTrainingMinutes,
    TrainingSessionType,
    TrainingParticipationType,
)


def training_minutes_entry(request):

    teams = Team.objects.all().order_by("name")
    other_teams = Team.objects.all().order_by("name")

    selected_team = None
    players = []
    training_session = None

    # ==========================================================
    # LOAD PLAYERS
    # ==========================================================

    if request.method == "GET":

        team_id = request.GET.get("team")
        date = request.GET.get("date")
        session_type = request.GET.get("session")

        if team_id:

            selected_team = get_object_or_404(
                Team,
                id=team_id
            )

            players = Player.objects.filter(
                team=selected_team
            ).order_by(
                "name",
                "second_name",
                "surname"
            )


            # If date and session are supplied,
            # check whether this training session already exists.

            if date and session_type:

                training_session = TrainingMinutes.objects.filter(
                    team=selected_team,
                    date=date,
                    session=session_type
                ).first()


    # ==========================================================
    # SAVE TRAINING MINUTES
    # ==========================================================

    elif request.method == "POST":

        team_id = request.POST.get("team")
        date = request.POST.get("date")
        session_type = request.POST.get("session")

        selected_team = get_object_or_404(
            Team,
            id=team_id
        )

        # Create or retrieve training session

        training_session, created = TrainingMinutes.objects.get_or_create(
            team=selected_team,
            date=date,
            session=session_type,
            defaults={
                "total_minutes": 0,
            },
        )

        # Get players from selected team

        players = Player.objects.filter(
            team=selected_team
        ).order_by(
            "name",
            "second_name",
            "surname"
        )

        total_minutes = 0

        # ======================================================
        # SAVE EACH PLAYER
        # ======================================================

        for player in players:

            minutes = request.POST.get(
                f"minutes_{player.id}",
                0
            )

            participation_type = request.POST.get(
                f"participation_{player.id}",
                TrainingParticipationType.REGULAR
            )

            trained_with_team_id = request.POST.get(
                f"trained_with_team_{player.id}"
            )

            trained_with_team = None

            # ======================================================
            # DETERMINE TEAM WHERE PLAYER TRAINED
            # ======================================================

            if participation_type == TrainingParticipationType.REGULAR:

                # Regular = trained with the selected team
                trained_with_team = selected_team

            elif (
                participation_type == TrainingParticipationType.OTHER_TEAM
                and trained_with_team_id
            ):

                # Other Team = trained with the selected other team
                trained_with_team = Team.objects.filter(
                    id=trained_with_team_id
                ).first()

            try:
                minutes = int(minutes or 0)
            except (TypeError, ValueError):
                minutes = 0

            # Make sure minutes are not negative

            minutes = max(minutes, 0)

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

        # Update session total
        training_session.total_minutes = total_minutes

        training_session.save( update_fields=["total_minutes"])
        messages.success(request, "Training minutes saved successfully.")

        return redirect("reports_app:training_minutes_entry")


    context = {
        "teams": teams,
        "other_teams": other_teams,
        "selected_team": selected_team,
        "players": players,
        "training_session": training_session,
        "session_types": TrainingSessionType.choices,
        "participation_types": TrainingParticipationType.choices,
    }

    return render(request, "training_minutes/training_minutes_entry.html",context)