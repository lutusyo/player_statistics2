# tagging_app_v2/views.py
from collections import defaultdict
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from matches_app.models import Match
from tagging_app_v2.models import PassEvent_v2





@login_required
def pass_network_dashboard(request, match_id):
    match = get_object_or_404(Match, id=match_id)

    events = (
        PassEvent_v2.objects.filter(match=match)
        .select_related(
            "actor__player",
            "receiver__player",
            "actor__team",
        )
        .order_by("timestamp", "created_at")
    )

    # team -> from_player -> to_player -> count
    raw_matrix = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    team_players = defaultdict(set)

    for e in events:
        if not e.receiver:
            continue

        team = e.actor.team
        from_p = e.actor
        to_p = e.receiver

        team_players[team].add(from_p)
        team_players[team].add(to_p)

        raw_matrix[team][from_p][to_p] += 1

    # ===== PREPARE TEMPLATE-FRIENDLY STRUCTURE =====
    pass_matrices = []

    for team, players in team_players.items():
        players = sorted(players, key=lambda x: x.player.name)

        rows = []
        for from_p in players:
            row = {
                "from": from_p,
                "cells": []
            }
            for to_p in players:
                row["cells"].append(
                    raw_matrix[team][from_p].get(to_p, 0)
                )
            rows.append(row)

        pass_matrices.append({
            "team": team,
            "players": players,
            "rows": rows,
        })

    context = {
        "match": match,
        "pass_events": events,
        "pass_matrices": pass_matrices,
    }

    return render(
        request,
        "tagging_app_v2/pass_network_dashboard.html",
        context
    )


