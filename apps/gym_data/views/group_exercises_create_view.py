from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from ..models import GymSession, Exercise, GroupExercise


def group_exercises_create(request, session_id):

    session = get_object_or_404(
        GymSession.objects.select_related("team"),
        id=session_id,
    )

    groups = list(
        session.groups
        .select_related("gym_type")
        .prefetch_related("players")
    )

    exercises = (
        Exercise.objects
        .select_related("category")
        .order_by("category__name", "name")
    )

    if request.method == "POST":

        row_count = int(request.POST.get("row_count", 0))

        with transaction.atomic():

            for row_index in range(row_count):

                exercise_id = request.POST.get(
                    f"exercise_{row_index}"
                )

                if not exercise_id:
                    continue

                exercise = get_object_or_404(
                    Exercise,
                    id=exercise_id,
                )

                for group in groups:

                    weight = request.POST.get(
                        f"weight_{row_index}_{group.id}"
                    )

                    sets = request.POST.get(
                        f"sets_{row_index}_{group.id}"
                    ) or 3

                    reps = request.POST.get(
                        f"reps_{row_index}_{group.id}"
                    ) or 8

                    # If no weight was entered for this group,
                    # don't create an exercise record.
                    if not weight:
                        continue

                    GroupExercise.objects.update_or_create(
                        gym_group=group,
                        exercise=exercise,
                        defaults={
                            "weight_kg": weight,
                            "sets": sets,
                            "reps": reps,
                        },
                    )

        messages.success(
            request,
            "All exercises were saved successfully.",
        )

        return redirect(
            "gym_data:gym_session_detail",
            session_id=session.id,
        )

    context = {
        "session": session,
        "groups": groups,
        "exercises": exercises,
    }

    return render(
        request,
        "gym_data/group_exercises_form.html",
        context,
    )