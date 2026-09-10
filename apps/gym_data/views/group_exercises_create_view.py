from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from ..forms import GroupExerciseFormSet
from ..models import GymGroup


def group_exercises_create(request, group_id):
    """
    Add multiple exercises to one gym group.
    """

    group = get_object_or_404(
        GymGroup.objects.select_related(
            "gym_session",
            "gym_session__team",
            "gym_type",
        ),
        id=group_id,
    )

    if request.method == "POST":

        formset = GroupExerciseFormSet(
            request.POST,
            queryset=group.exercises.all(),
        )

        if formset.is_valid():

            exercises = formset.save(commit=False)

            for exercise in exercises:
                exercise.gym_group = group
                exercise.save()

            for deleted_exercise in formset.deleted_objects:
                deleted_exercise.delete()

            messages.success(
                request,
                "Exercises recorded successfully.",
            )

            return redirect(
                "gym_data:gym_session_detail",
                session_id=group.gym_session.id,
            )

    else:

        formset = GroupExerciseFormSet(
            queryset=group.exercises.all(),
        )

    context = {
        "group": group,
        "formset": formset,
    }

    return render(
        request,
        "gym_data/group_exercises_form.html",
        context,
    )