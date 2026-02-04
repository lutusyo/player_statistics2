# tagging_app_v2/views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from matches_app.models import Match
from tagging_app_v2.models import PassEvent_v2
from lineup_app.models import MatchLineup
from tagging_app_v2.forms import PassEventV2Form


@login_required
def pass_events_v2_list(request, match_id):
    match = get_object_or_404(Match, id=match_id)

    pass_events = ( PassEvent_v2.objects.filter(match=match)
        .select_related(
            "actor__player",
            "target__player",
            "receiver__player"
        )
        .order_by("timestamp", "created_at")
    )

    context = {
        "match": match,
        "pass_events": pass_events,
    }

    return render(request, "tagging_app_v2/pass_network_dashboard.html", context )
