from django.contrib import messages
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, redirect, render

from ..forms import ( GymSessionForm, GymGroupForm, GroupExerciseForm, GymReportFilterForm,)
from ..models import (GymSession, GymGroup, GroupExercise,)


def group_exercise_create(request, group_id):
    """
    Add an exercise to a gym group.
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

        form = GroupExerciseForm(request.POST)

        if form.is_valid():

            exercise = form.save(commit=False)
            exercise.gym_group = group
            exercise.save()

            messages.success(request, "Exercise recorded successfully.",)
            return redirect("gym_data:gym_session_detail", session_id=group.gym_session.id,)

    else:
        form = GroupExerciseForm()

    context = {
                "form": form,
                "group": group,
            }

    return render(request, "gym_data/exercise_form.html", context,)


