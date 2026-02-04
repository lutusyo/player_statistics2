from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from matches_app.models import Match
from tagging_app_v2.models import PassEvent_v2
from lineup_app.models import MatchLineup, Substitution
from tagging_app_v2.forms import PassEventV2Form
from django.db.models import Q


@login_required
def create_pass_event_v2(request, match_id):
    match = get_object_or_404(Match, id=match_id)

    # ---------- AJAX SAVE ----------
    if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":

        actor_id = request.POST.get("actor")
        receiver_id = request.POST.get("receiver")
        target_id = request.POST.get("target")  # may be None
        action_type = request.POST.get("action_type")

        if not all([actor_id, receiver_id, action_type]):
            return JsonResponse(
                {"success": False, "error": "Missing required data"},
                status=400
            )

        try:
            actor = MatchLineup.objects.get(id=actor_id)
            receiver = MatchLineup.objects.get(id=receiver_id)

            target = None
            if target_id:
                target = MatchLineup.objects.get(id=target_id)

            PassEvent_v2.objects.create(
                match=match,
                actor=actor,
                receiver=receiver,
                target=target,
                action_type=action_type
            )

            return JsonResponse({"success": True})

        except Exception as e:
            return JsonResponse(
                {"success": False, "error": str(e)},
                status=500
            )


    # ---------- NORMAL PAGE LOAD ----------
    form = PassEventV2Form(match=match)

    # 🔥 Only players currently on pitch
    def players_on_pitch(team):
        # Starting players
        qs = MatchLineup.objects.filter(match=match, team=team, is_starting=True)

        # Include substitutes who came in and haven't gone out yet
        subs_in = Substitution.objects.filter(match=match, player_in__team=team)
        for sub in subs_in:
            # Remove player_out from the list
            qs = qs.exclude(id=sub.player_out.id)
            # Add player_in if not already included
            qs |= MatchLineup.objects.filter(id=sub.player_in.id)

        return qs.order_by('order', 'player__name')

    home_lineups = players_on_pitch(match.home_team)
    away_lineups = players_on_pitch(match.away_team)

    

    # Positions (for possible future pitch layout)
    home_forwards = ["LW", "ST", "RW"]
    home_midfield = ["LCM", "CM", "RCM"]
    home_defence = ["LB", "LCB", "RCB", "RB"]
    home_goalkeeper = ["GK"]

    away_forwards = ["LW", "ST", "RW"]
    away_midfield = ["LCM", "CM", "RCM"]
    away_defence = ["LB", "LCB", "RCB", "RB"]
    away_goalkeeper = ["GK"]

    context = {
        "form": form,
        "match": match,
        "home_lineups": home_lineups,
        "away_lineups": away_lineups,
        "home_forwards": home_forwards,
        "home_midfield": home_midfield,
        "home_defence": home_defence,
        "home_goalkeeper": home_goalkeeper,
        "away_forwards": away_forwards,
        "away_midfield": away_midfield,
        "away_defence": away_defence,
        "away_goalkeeper": away_goalkeeper,
    }

    return render(request, "tagging_app_v2/pass_network_enter_data.html", context)
