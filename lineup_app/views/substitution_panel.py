from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_POST
from django.db import transaction
from django.db.models import Q
import json
from lineup_app.models import Match, MatchLineup, Substitution
from players_app.models import Player

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from lineup_app.models import Match, MatchLineup, Substitution

from django.db import transaction



# Helper to serialize MatchLineup row for JSON
def _serialize_lineup(lineup):
    player = lineup.player
    return {
        "lineup_id": lineup.id,
        "player_id": player.id,
        "name": player.name,
        "jersey_number": player.jersey_number,
        "photo_url": player.photo.url if player.photo else "",
        "is_starting": lineup.is_starting,
        "time_in": lineup.time_in,
        "time_out": lineup.time_out,
        "minutes_played": lineup.minutes_played,
        "team": lineup.team.name if lineup.team else None,
    }




@require_http_methods(["GET"])
def api_get_lists(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    lineups = MatchLineup.objects.filter(match=match).select_related("player", "team")

    def group_team(team_obj):
        team_lineups = lineups.filter(team=team_obj)

        # Include all players on pitch (time_out=None)
        on_field = team_lineups.filter(time_out__isnull=True)
        on_bench = team_lineups.filter(is_starting=False, time_in__isnull=True)
        subbed_out = team_lineups.filter(time_out__isnull=False)

        all_team_players = Player.objects.filter(team=team_obj)
        selected_player_ids = team_lineups.values_list("player_id", flat=True)
        not_selected = all_team_players.exclude(id__in=selected_player_ids)

        return {
            "on_field": [_serialize_lineup(l) for l in on_field],
            "on_bench": [_serialize_lineup(l) for l in on_bench],
            "subbed_out": [_serialize_lineup(l) for l in subbed_out],
            "not_selected": [
                {
                    "lineup_id": None,
                    "player_id": p.id,
                    "name": p.name,
                    "jersey_number": p.jersey_number,
                    "photo_url": p.photo.url if p.photo else "",
                    "is_starting": False,
                    "time_in": None,
                    "time_out": None,
                    "minutes_played": 0,
                    "team": p.team.name if p.team else None,
                }
                for p in not_selected
            ],
        }

    team_a = group_team(match.home_team)
    team_b = group_team(match.away_team)

    # Ensure all starting players are included
    starting_eleven = [
        p for p in team_a["on_field"] if p["is_starting"]
    ] + [
        p for p in team_b["on_field"] if p["is_starting"]
    ]

    data = {
        "home": {
            "currently_on_pitch": team_a["on_field"],
            "currently_on_subs": team_a["on_bench"],
            "bench": team_a["not_selected"],
            "already_played_and_out": team_a["subbed_out"],
            "starting_eleven": [p for p in team_a["on_field"] if p["is_starting"]],
        },
        "away": {
            "currently_on_pitch": team_b["on_field"],
            "currently_on_subs": team_b["on_bench"],
            "bench": team_b["not_selected"],
            "already_played_and_out": team_b["subbed_out"],
            "starting_eleven": [p for p in team_b["on_field"] if p["is_starting"]],
        },
        "subs_exchanges": [],  # Keep as-is
        "subs_this_match": [],
        "subs_not_played": [],
    }


    # Fill subs_exchanges
    substitutions = Substitution.objects.filter(match=match).select_related(
        "player_in__player", "player_out__player"
    ).order_by('minute')

    data["subs_exchanges"] = [
        {
            "player_out": {
                "name": sub.player_out.player.name,
                "photo_url": sub.player_out.player.photo.url if sub.player_out.player.photo else "",
                "time_out": sub.player_out.time_out,
            },
            "player_in": {
                "name": sub.player_in.player.name,
                "photo_url": sub.player_in.player.photo.url if sub.player_in.player.photo else "",
                "time_in": sub.player_in.time_in,
            },
            "minute": sub.minute,
        }
        for sub in substitutions
    ]

    return JsonResponse(data)



@require_POST
@transaction.atomic
def api_finalize_substitution(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    body = json.loads(request.body)

    player_out_id = body.get("player_out_id")
    player_in_id = body.get("player_in_id")
    minute = body.get("minute")

    if not all([player_out_id, player_in_id, minute is not None]):
        return JsonResponse({"error": "Missing required data"}, status=400)

    lineup_out = get_object_or_404(MatchLineup, match=match, player_id=player_out_id)
    lineup_in = get_object_or_404(MatchLineup, match=match, player_id=player_in_id)

    lineup_out.time_out = minute
    lineup_in.time_in = minute

    lineup_out.save()
    lineup_in.save()

    Substitution.objects.create(
        match=match,
        player_out=lineup_out,
        player_in=lineup_in,
        minute=minute
    )

    return JsonResponse({"success": True})


@require_POST
@transaction.atomic
def api_undo_substitution(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    last_sub = Substitution.objects.filter(match=match).order_by("-id").first()
    if not last_sub:
        return JsonResponse({"error": "No substitutions to undo"}, status=400)

    last_sub.player_out.time_out = None
    last_sub.player_out.save()

    last_sub.player_in.time_in = None
    last_sub.player_in.save()

    last_sub.delete()

    return JsonResponse({"success": True})


# lineup_app/views/substitution.py
@require_POST
@transaction.atomic
def api_finalize_match(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    # Update remaining players on pitch
    lineups = MatchLineup.objects.filter(match=match, time_out__isnull=True)
    current_minute = request.POST.get("minute")  # or pass in body
    for lineup in lineups:
        lineup.time_out = current_minute or 90  # default to 90 if not provided
        lineup.save()
    return JsonResponse({"success": True})

def substitution_panel(request, match_id):
    match = get_object_or_404(Match, id=match_id)

    # Current on pitch
    home_on_pitch = MatchLineup.objects.filter(
        match=match, team=match.home_team, time_in__isnull=False, time_out__isnull=True
    )
    away_on_pitch = MatchLineup.objects.filter(
        match=match, team=match.away_team, time_in__isnull=False, time_out__isnull=True
    )

    # Bench players
    home_lineup_ids = MatchLineup.objects.filter(match=match, team=match.home_team).values_list("player_id", flat=True)
    away_lineup_ids = MatchLineup.objects.filter(match=match, team=match.away_team).values_list("player_id", flat=True)

    def get_bench(team, lineup_ids):
        bench_lineup = MatchLineup.objects.filter(match=match, team=team, is_starting=False)
        not_selected = Player.objects.filter(team=team).exclude(id__in=lineup_ids)

        bench = []
        for l in bench_lineup:
            bench.append({
                "id": l.id,
                "name": l.player.name,
                "position": l.position,
                "is_lineup": True,
            })
        for p in not_selected:
            bench.append({
                "id": p.id,
                "name": p.name,
                "position": "SUB",
                "is_lineup": False,
            })
        return bench

    home_bench = get_bench(match.home_team, home_lineup_ids)
    away_bench = get_bench(match.away_team, away_lineup_ids)

    substitutions = Substitution.objects.filter(match=match).select_related(
        "player_out", "player_in"
    )

    if request.method == "POST":
        player_out_id = request.POST.get("player_out")
        player_in_id = request.POST.get("player_in")
        minute = request.POST.get("minute")

        if not (player_out_id and player_in_id and minute):
            messages.error(request, "Please select players and enter minute.")
        else:
            with transaction.atomic():
                player_out = get_object_or_404(MatchLineup, id=player_out_id)

                # If player_in is a Player (not yet in lineup), create a lineup entry
                if MatchLineup.objects.filter(match=match, player_id=player_in_id).exists():
                    # The player is already in lineup for this match
                    player_in = MatchLineup.objects.get(match=match, player_id=player_in_id)
                else:
                    player_obj = get_object_or_404(Player, id=player_in_id)
                    player_in = MatchLineup.objects.create(
                        match=match,
                        team=player_obj.team,
                        player=player_obj,
                        is_starting=False,
                        time_in=None,
                        time_out=None,
                    )


                player_out.time_out = minute
                player_in.time_in = minute
                player_out.save()
                player_in.save()

                Substitution.objects.create(
                    match=match,
                    player_out=player_out,
                    player_in=player_in,
                    minute=minute,
                )

            messages.success(
                request,
                f"Substitution recorded: {player_out.player.name} → {player_in.player.name}",
            )
            return redirect("lineup_app:substitution_panel", match_id=match.id)

    # ✅ Ensure we always return an HttpResponse
    return render(
        request,
        "lineup_app/substitution_panel.html",
        {
            "match": match,
            "home_currently_on_pitch": home_on_pitch,
            "home_bench": home_bench,
            "away_currently_on_pitch": away_on_pitch,
            "away_bench": away_bench,
            "substitutions": substitutions,
        },
    )


