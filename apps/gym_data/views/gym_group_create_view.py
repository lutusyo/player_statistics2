from django.contrib import messages
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, redirect, render

from ..forms import (
    GymSessionForm,
    GymGroupForm,
    GroupExerciseForm,
    GymReportFilterForm,
)

from ..models import (GymSession, GymGroup, GroupExercise,)

def gym_group_create(request, session_id):
    """
    Add a gym type/group to a session.
    """

    session = get_object_or_404(
        GymSession,
        id=session_id,
    )

    if request.method == "POST":

        form = GymGroupForm(request.POST)

        if form.is_valid():

            group = form.save(commit=False)
            group.gym_session = session
            group.save()

            form.save_m2m()

            messages.success(
                request,
                "Gym group created successfully.",
            )

            return redirect(
                "gym_app:gym_session_detail",
                session_id=session.id,
            )

    else:
        form = GymGroupForm()

    return render(
        request,
        "gym_app/group_form.html",
        {
            "form": form,
            "session": session,
        },
    )


