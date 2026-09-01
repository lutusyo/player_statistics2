from django.contrib import messages
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, redirect, render

from ..forms import ( GymSessionForm, GymGroupForm, GroupExerciseForm, GymReportFilterForm,)
from ..models import ( GymSession, GymGroup, GroupExercise,)

def gym_report(request):
    """
    Filter and display gym reports.
    """

    form = GymReportFilterForm(request.GET or None)

    exercises = (GroupExercise.objects.select_related(
            "gym_group",
            "gym_group__gym_session",
            "gym_group__gym_session__team",
            "gym_group__gym_type",
            "exercise",
            "exercise__category",
        )
        .prefetch_related("gym_group__players",)
        .order_by(
            "-gym_group__gym_session__date",
            "gym_group__gym_session__team",
            "gym_group__gym_type",
        )
    )

    if form.is_valid():

        team = form.cleaned_data.get("team")
        start_date = form.cleaned_data.get("start_date")
        end_date = form.cleaned_data.get("end_date")
        category = form.cleaned_data.get("category")
        exercise = form.cleaned_data.get("exercise")

        if team:
            exercises = exercises.filter(gym_group__gym_session__team=team)

        if start_date:
            exercises = exercises.filter(gym_group__gym_session__date__gte=start_date)

        if end_date:
            exercises = exercises.filter(gym_group__gym_session__date__lte=end_date)

        if category:
            exercises = exercises.filter( exercise__category=category)

        if exercise:
            exercises = exercises.filter(exercise=exercise)

    context = {
            "form": form,
            "exercises": exercises,
            }

    return render(request, "gym_data/report.html", context,)