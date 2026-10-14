
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
        session.groups.select_related("gym_type").prefetch_related("players")
    )

    exercises = Exercise.objects.select_related("category").order_by(
        "category__name", "name"
    )

    # Existing exercises saved for this session's groups.
    saved_by_exercise = {}

    saved_records = (
        GroupExercise.objects
        .filter(gym_group__in=groups)
        .select_related("exercise", "gym_group", "gym_group__gym_type")
        .order_by("exercise__name", "gym_group__gym_type__name")
    )

    for record in saved_records:
        exercise_id = record.exercise_id

        if exercise_id not in saved_by_exercise:
            saved_by_exercise[exercise_id] = {
                "exercise": record.exercise,
                "groups": [],
            }

        saved_by_exercise[exercise_id]["groups"].append({
            "name": record.gym_group.gym_type.name,
            "weight": record.weight_kg,
            "sets": record.sets,
            "reps": record.reps,
        })

    if request.method == "POST":
        try:
            row_count = min(max(int(request.POST.get("row_count", 0)), 0), 200)
        except (TypeError, ValueError):
            row_count = 0

        with transaction.atomic():
            for row_index in range(row_count):
                exercise_id = request.POST.get(f"exercise_{row_index}")

                if not exercise_id:
                    continue

                exercise = get_object_or_404(Exercise, id=exercise_id)

                for group in groups:
                    weight = request.POST.get(f"weight_{row_index}_{group.id}")

                    if weight in (None, ""):
                        continue

                    sets = request.POST.get(f"sets_{row_index}_{group.id}") or 3
                    reps = request.POST.get(f"reps_{row_index}_{group.id}") or 8

                    GroupExercise.objects.update_or_create(
                        gym_group=group,
                        exercise=exercise,
                        defaults={
                            "weight_kg": weight,
                            "sets": sets,
                            "reps": reps,
                        },
                    )

        messages.success(request, "Exercises saved successfully.")
        return redirect("gym_data:gym_session_detail", session_id=session.id)

    context = {
        "session": session,
        "groups": groups,
        "exercises": exercises,
        "saved_exercises": list(saved_by_exercise.values()),
    }

    return render(request, "gym_data/group_exercises_form.html", context)
