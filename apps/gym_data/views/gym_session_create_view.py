from django.contrib import messages
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, redirect, render

from ..forms import (GymSessionForm, GymGroupForm, GroupExerciseForm, GymReportFilterForm,)
from ..models import (GymSession, GymGroup, GroupExercise, )
from .gym_dashboard_view import gym_dashboard

def gym_session_create(request):
    """
    Create a new gym session.
    """

    if request.method == "POST":
        form = GymSessionForm(request.POST)

        if form.is_valid():
            session = form.save()

            messages.success(request, "Gym session created successfully.",)
            return redirect("gym_data:gym_session_detail", session_id=session.id,)

    else:
        form = GymSessionForm()

    context = {
                "form": form,
            }

    return render(request,"gym_data/session_form.html", context,)


