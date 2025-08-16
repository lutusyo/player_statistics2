from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_POST
from django.db import transaction
from django.db.models import Q
import json
from lineup_app.models import Match, MatchLineup, Substitution
from players_app.models import Player


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
def substitution_panel(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    return render(request, "matches_app/substitution_panel.html", {"match": match})


@require_http_methods(["GET"])
def api_get_lists(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    lineups = MatchLineup.objects.filter(match=match).select_related("player", "team")

    def group_team(team_obj):
        team_lineups = lineups.filter(team=team_obj)

        on_field = team_lineups.filter(time_out__isnull=True).filter(Q(is_starting=True) | Q(time_in__isnull=False))
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

    # Flattened data for frontend
    data = {
        "currently_on_pitch": team_a["on_field"] + team_b["on_field"],
        "currently_on_subs": team_a["on_bench"] + team_b["on_bench"],
        "bench": team_a["not_selected"] + team_b["not_selected"],
        "already_played_and_out": team_a["subbed_out"] + team_b["subbed_out"],
        "starting_eleven": [p for p in team_a["on_field"] if p["is_starting"]] + [p for p in team_b["on_field"] if p["is_starting"]],
        "subs_this_match": [],  # Add logic if you want to track
        "subs_exchanges": [],
        "subs_not_played": [],  # Add logic if you want to track
    }

    # Fill subs_exchanges with actual substitutions made
    substitutions = Substitution.objects.filter(match=match).select_related("player_in__player", "player_out__player").order_by('minute')
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
