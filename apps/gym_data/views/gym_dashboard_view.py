from django.contrib import messages
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, redirect, render

from ..forms import ( GymSessionForm, GymGroupForm, GroupExerciseForm, GymReportFilterForm,)
from ..models import (GymSession, GymGroup, GroupExercise,)

def gym_dashboard(request):
    """
    Main gym dashboard.
    """

    sessions = (GymSession.objects.select_related("team")
        .prefetch_related("groups__gym_type", "groups__players", "groups__exercises__exercise__category",)
    )

    context = {"sessions": sessions,
            }

    return render(request, "gym_data/dashboard.html", context,)

