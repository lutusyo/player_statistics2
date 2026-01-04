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
            receiver = form.cleaned_data["receiver"]
            action_type = form.cleaned_data["action_type"]
            timestamp = form.cleaned_data.get("timestamp")

            # Save the base event (what analyst actually tagged)
            event = PassEvent_v2.objects.create(
                match=match,
                actor=actor,
                receiver=receiver,
                action_type=action_type,
                timestamp=timestamp,
            )

            # --------------------------------
            # DERIVED LOGIC (NO USER INPUT)
            # --------------------------------

            actor_team = actor.team.team_type
            receiver_team = receiver.team.team_type

            # 1️⃣ PASS / BALL LOST LOGIC
            if actor_team == "OUR_TEAM":

                if action_type == "SHORT_PASS":
                    if receiver_team == "OUR_TEAM":
                        # PASS COMPLETED
                        # (later → increment completed pass stat)
                        pass
                    else:
                        # BALL LOST
                        # (later → increment ball lost stat)
                        pass

            # 2️⃣ AERIAL DUEL LOGIC (AUTO)
            if actor_team == "OUR_TEAM" and action_type in [
                "LONG_PASS",
                "GOAL_KICK",
                "CLEARANCE",
                "CROSS",
                "LONG_THROW_IN",
            ]:
                if receiver_team == "OUR_TEAM":
                    # AERIAL DUEL WON (receiver)
                    # (later → increment aerial won for receiver.player)
                    pass
                else:
                    # AERIAL DUEL LOST
                    # (later → increment aerial lost)
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
