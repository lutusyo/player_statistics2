#gym_session_create_view.py
from django.contrib import messages
from django.shortcuts import redirect, render

from ..forms import GymSessionForm


def gym_session_create(request):
    """
    Create a new gym session.
    """

    if request.method == "POST":
        form = GymSessionForm(request.POST)

        if form.is_valid():
            session = form.save()

            messages.success(
                request,
                "Gym session created successfully.",
            )

            return redirect(
                "gym_data:gym_session_detail",
                session_id=session.id,
            )

    else:
        form = GymSessionForm()

    context = {
        "form": form,
    }

    return render(
        request,
        "gym_data/session_form.html",
        context,
    )
