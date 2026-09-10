#gym_group_create_view.py

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from ..forms import GymGroupForm
from ..models import GymSession


def gym_group_create(request, session_id):

    session = get_object_or_404(
        GymSession.objects.select_related("team"),
        id=session_id,
    )

    if request.method == "POST":
        form = GymGroupForm(
            request.POST,
            team=session.team,
        )

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
                "gym_data:gym_session_detail",
                session_id=session.id,
            )

    else:
        form = GymGroupForm(
            team=session.team,
        )

    context = {
        "form": form,
        "session": session,
    }

    return render(
        request,
        "gym_data/group_form.html",
        context,
    )
