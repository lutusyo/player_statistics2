from django.contrib import messages
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, redirect, render

from ..forms import (GymSessionForm, GymGroupForm, GroupExerciseForm, GymReportFilterForm,)
from ..models import (GymSession, GymGroup, GroupExercise, )

def gym_session_detail(request, session_id):
    """
    Display one gym session.
    """
    session = get_object_or_404(GymSession.objects.select_related("team"), id=session_id,)
    groups = (session.groups.select_related("gym_type").prefetch_related("players","exercises__exercise__category",))

    context =  {
                "session": session,
                "groups": groups,
    }

    return render(request, "gym_data/session_detail.html", context,)


