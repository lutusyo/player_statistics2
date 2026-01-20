# tagging_app_v2/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from matches_app.models import Match
from tagging_app_v2.forms import PassEventV2Form
from tagging_app_v2.models import PassEvent_v2


@login_required
def create_pass_event_v2(request, match_id):
    match = get_object_or_404(Match, id=match_id)

    if request.method == "POST":
        form = PassEventV2Form(request.POST, match=match)
        if form.is_valid():

            actor = form.cleaned_data["actor"]
            target = form.cleaned_data["target"]
            receiver = form.cleaned_data["receiver"]
            action_type = form.cleaned_data["action_type"]
            timestamp = form.cleaned_data.get("timestamp")

            event = PassEvent_v2.objects.create(
                match=match,
                actor=actor,
                target=target,
                receiver=receiver,
                action_type=action_type,
                timestamp=timestamp,
            )

            # ---------------------------
            # DERIVED LOGIC
            # ---------------------------

            actor_team = actor.team.team_type
            receiver_team = receiver.team.team_type if receiver else None

            # PASS SUCCESS
            if target and receiver:
                if target == receiver:
                    # completed pass
                    pass
                else:
                    # failed pass / interception
                    pass

            # AERIAL DUEL AUTO TAG
            if action_type in [
                "LONG_PASS",
                "GOAL_KICK",
                "CLEARANCE",
                "CROSS",
                "LONG_THROW_IN",
            ]:
                if receiver and receiver.team.team_type == actor_team:
                    # aerial duel won
                    pass
                else:
                    # aerial duel lost
                    pass

            return redirect("tagging_app_v2:tag_panel_v2", match_id=match.id)

    else:
        form = PassEventV2Form(match=match)

    return render(
        request,
        "tagging_app_v2/pass_network_enter_data.html",
        {
            "form": form,
            "match": match,
        },
    )
