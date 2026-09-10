#gym_dashboard_view.py
from django.shortcuts import render

from ..models import GymSession


def gym_dashboard(request):
    """
    Main gym dashboard.
    """

    sessions = (
        GymSession.objects
        .select_related("team")
        .prefetch_related(
            "groups__gym_type",
            "groups__players",
            "groups__exercises__exercise__category",
        )
    )

    context = {
        "sessions": sessions,
    }

    return render(
        request,
        "gym_data/dashboard.html",
        context,
    )
