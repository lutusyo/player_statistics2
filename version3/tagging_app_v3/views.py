from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q

from .models import MatchEvent
from version1.matches_app.models import Match
from version1.lineup_app.models import MatchLineup, Substitution

from version3.tagging_app_v3.constants import (
    MatchPeriod, EventType,
    OutcomeChoices, BodyPartChoices, LocationChoices
)
from version3.tagging_app_v3.constants import BALL_ACTION_CHOICES, FOUL_OUTCOME


@login_required
def create_match_event(request, match_id):
    match = get_object_or_404(Match, id=match_id)

    # =========================
    # AJAX SAVE
    # =========================
    if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":

        actor_id = request.POST.get("actor")
        receiver_id = request.POST.get("receiver")
        event_type = request.POST.get("event_type")
        action_type = request.POST.get("action_type")
        foul_outcome = request.POST.get("foul_outcome")

        outcome = request.POST.get("outcome")
        body_part = request.POST.get("body_part")
        location_tag = request.POST.get("location_tag")

        minute = request.POST.get("minute") or 0
        second = request.POST.get("second") or 0

        is_own_goal = request.POST.get("is_own_goal") in ["true", "on", "1"]

        # ---------- VALIDATION ----------
        if not actor_id or not event_type:
            return JsonResponse(
                {"success": False, "error": "Actor and event type are required"},
                status=400
            )

        if event_type == "ball_action" and not action_type:
            return JsonResponse(
                {"success": False, "error": "Action type required for ball actions"},
                status=400
            )

        if action_type == "FOUL" and not foul_outcome:
            return JsonResponse(
                {"success": False, "error": "Foul outcome required"},
                status=400
            )

        if event_type == "shot" and not outcome:
            return JsonResponse(
                {"success": False, "error": "Shot outcome required"},
                status=400
            )

        try:
            actor = MatchLineup.objects.get(id=actor_id)
            receiver = MatchLineup.objects.get(id=receiver_id) if receiver_id else None

            MatchEvent.objects.create(
                match=match,
                team=actor.team,
                actor=actor,
                receiver=receiver,
                event_type=event_type,

                minute=minute,
                second=second,

                action_type=action_type,
                foul_outcome=foul_outcome if action_type == "FOUL" else None,

                outcome=outcome,
                body_part=body_part,
                location_tag=location_tag,

                is_own_goal=is_own_goal
            )

            return JsonResponse({"success": True})

        except Exception as e:
            return JsonResponse(
                {"success": False, "error": str(e)},
                status=500
            )

    # =========================
    # PLAYERS ON PITCH LOGIC
    # =========================
    def players_on_pitch(team):
        qs = MatchLineup.objects.filter(
            match=match,
            team=team,
            is_starting=True
        )

        subs_in = Substitution.objects.filter(match=match, player_in__team=team)

        for sub in subs_in:
            qs = qs.exclude(id=sub.player_out.id)
            qs |= MatchLineup.objects.filter(id=sub.player_in.id)

        return qs.order_by("order", "player__name")

    home_lineups = players_on_pitch(match.home_team)
    away_lineups = players_on_pitch(match.away_team)

    # =========================
    # POSITION GROUPING (UI)
    # =========================
    forwards = ["LW", "ST", "RW"]
    midfield = ["LCM", "CM", "RCM"]
    defence = ["LB", "LCB", "RCB", "RB"]
    goalkeeper = ["GK"]

    context = {
        "match": match,

        "home_lineups": home_lineups,
        "away_lineups": away_lineups,

        "forwards": forwards,
        "midfield": midfield,
        "defence": defence,
        "goalkeeper": goalkeeper,

        "event_types": EventType.choices,
        "ball_actions": BALL_ACTION_CHOICES,
        "foul_outcomes": FOUL_OUTCOME,
        "outcomes": OutcomeChoices.choices,
        "body_parts": BodyPartChoices.choices,
        "locations": LocationChoices.choices,
    }

    return render(request, "tagging_app_v3/pass_network_enter_data.html", context)