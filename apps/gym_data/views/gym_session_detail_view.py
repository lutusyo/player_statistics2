#gym_session_details_view.py

from django.shortcuts import get_object_or_404, render

from ..models import GymSession


def gym_session_detail(request, session_id):
    """
    Display one gym session.
    """

    session = get_object_or_404(
        GymSession.objects.select_related("team"),
        id=session_id,
    )

    groups = (
        session.groups
        .select_related("gym_type")
        .prefetch_related(
            "players",
            "exercises__exercise__category",
        )
    )

    context = {
        "session": session,
        "groups": groups,
    }

    return render(
        request,
        "gym_data/session_detail.html",
        context,
    )

