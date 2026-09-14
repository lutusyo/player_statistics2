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

from django.urls import reverse
from urllib.parse import urlencode

def training_minutes_entry(request):

    # ==========================================================
    # OUR / HOME TEAMS
    # ==========================================================

    teams = (
        Team.objects
        .filter(team_type="OUR_TEAM")
        .select_related("age_group")
        .order_by(
            "age_group__code",
            "name"
        )
    )

    # ==========================================================
    # OTHER INTERNAL TEAMS
    # ==========================================================

    other_teams = (
        Team.objects
        .filter(team_type="OUR_TEAM")
        .select_related("age_group")
        .order_by(
            "age_group__code",
            "name"
        )
    )

    # ==========================================================
    # NATIONAL TEAMS
    # ==========================================================

    national_teams = (
        Team.objects
        .filter(team_category="NATIONAL")
        .select_related("age_group")
        .order_by(
            "age_group__code",
            "name"
        )
    )

    selected_team = None
    players = []
    training_session = None


    # ==========================================================
    # LOAD SESSION
    # ==========================================================

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
                Player.objects
                .filter(team=selected_team)
                .order_by(
                    "name",
                    "second_name",
                    "surname"
                )
            )


            # ==================================================
            # LOAD EXISTING SESSION
            # ==================================================

            if date and session_type:

                training_session = (
                    TrainingMinutes.objects
                    .filter(
                        team=selected_team,
                        date=date,
                        session=session_type
                    )
                    .first()
                )


                # ==================================================
                # ATTACH PLAYER TRAINING RECORDS
                # ==================================================

                if training_session:

                    records = (
                        PlayerTrainingMinutes.objects
                        .filter(
                            training_session=training_session
                        )
                        .select_related(
                            "trained_with_team"
                        )
                    )


                    record_map = {
                        record.player_id: record
                        for record in records
                    }


                    for player in players:

                        player.training_record = (
                            record_map.get(
                                player.id
                            )
                        )



    # ==========================================================
    # SAVE TRAINING MINUTES
    # ==========================================================

    elif request.method == "POST":

        team_id = request.POST.get("team")
        date = request.POST.get("date")
        session_type = request.POST.get("session")


        # ======================================================
        # VALIDATE MAIN TEAM
        # ======================================================

        selected_team = get_object_or_404(
            Team.objects.select_related("age_group"),
            id=team_id,
            team_type="OUR_TEAM",
        )


        # ======================================================
        # CREATE / GET TRAINING SESSION
        # ======================================================

        training_session, created = (
            TrainingMinutes.objects.get_or_create(
                team=selected_team,
                date=date,
                session=session_type,
                defaults={
                    "total_minutes": 0,
                },
            )
        )


        # ======================================================
        # GET PLAYERS
        # ======================================================

        players = (
            Player.objects
            .filter(team=selected_team)
            .order_by(
                "name",
                "second_name",
                "surname"
            )
        )


        total_minutes = 0


        # ======================================================
        # SAVE EACH PLAYER
        # ======================================================

        for player in players:

            # --------------------------------------------------
            # MINUTES
            # --------------------------------------------------

            minutes = request.POST.get(
                f"minutes_{player.id}",
                0
            )


            try:

                minutes = int(
                    minutes or 0
                )

            except (
                TypeError,
                ValueError
            ):

                minutes = 0


            minutes = max(
                minutes,
                0
            )


            # --------------------------------------------------
            # PARTICIPATION
            # --------------------------------------------------

            participation_type = request.POST.get(
                f"participation_{player.id}",
                TrainingParticipationType.REGULAR
            )


            # --------------------------------------------------
            # OTHER TEAM
            # --------------------------------------------------

            other_team_id = request.POST.get(
                f"trained_with_team_{player.id}"
            )


            # --------------------------------------------------
            # NATIONAL TEAM
            # --------------------------------------------------

            national_team_id = request.POST.get(
                f"national_team_{player.id}"
            )


            trained_with_team = None


            # ==================================================
            # REGULAR
            # ==================================================

            if (
                participation_type
                == TrainingParticipationType.REGULAR
            ):

                # The player trained with the
                # selected/main team.

                trained_with_team = selected_team


            # ==================================================
            # OTHER TEAM
            # ==================================================

            elif (
                participation_type
                == TrainingParticipationType.OTHER_TEAM
            ):

                if other_team_id:

                    trained_with_team = (
                        Team.objects
                        .filter(
                            id=other_team_id,
                            team_type="OUR_TEAM",
                        )
                        .first()
                    )


            # ==================================================
            # NATIONAL TEAM
            # ==================================================

            elif (
                participation_type
                == TrainingParticipationType.NATIONAL_TEAM
            ):

                if national_team_id:

                    trained_with_team = (
                        Team.objects
                        .filter(
                            id=national_team_id,
                            team_category="NATIONAL",
                        )
                        .first()
                    )


            # ==================================================
            # INDIVIDUAL / INJURED / ABSENT
            # ==================================================

            else:

                trained_with_team = None


            # ==================================================
            # FORCE ZERO MINUTES
            # ==================================================

            if participation_type in [
                TrainingParticipationType.INJURED,
                TrainingParticipationType.ABSENT,
            ]:

                minutes = 0


            # ==================================================
            # SAVE PLAYER RECORD
            # ==================================================

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


        # ======================================================
        # UPDATE SESSION TOTAL
        # ======================================================

        training_session.total_minutes = (
            total_minutes
        )

        training_session.save(
            update_fields=[
                "total_minutes"
            ]
        )


        messages.success(
            request,
            "Training minutes saved successfully."
        )


        # ======================================================
        # IMPORTANT:
        # REDIRECT WITH THE SAME SESSION INFORMATION
        # ======================================================

        return redirect("reports_app:training_minutes_entry")
            


    # ==========================================================
    # CONTEXT
    # ==========================================================

    context = {

        "teams": teams,

        "other_teams": other_teams,

        "national_teams": national_teams,

        "selected_team": selected_team,

        "players": players,

        "training_session": training_session,

        "session_types":
            TrainingSessionType.choices,

        "participation_types":
            TrainingParticipationType.choices,
    }


    return render(
        request,
        "training_minutes/training_minutes_entry.html",
        context
    )
