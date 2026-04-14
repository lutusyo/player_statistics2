from django.shortcuts import render, get_object_or_404
from django.db.models import Sum, Count, Q, Avg
from version2.loans_app_v2.models import LoanedPlayer


def loan_players_list_view(request):
    players = LoanedPlayer.objects.select_related("player", "loan_club") \
        .filter(is_active=True) \
        .order_by("player__name", "player__surname")

    return render(request, "loans_app_v2/loan_players_list.html", {
        "players": players
    })

def loan_player_detail_view(request, player_id):
    player = get_object_or_404(
        LoanedPlayer.objects.select_related("player", "loan_club"),
        id=player_id
    )

    daily_entries = player.daily_entries.select_related(
        "home_team", "away_team"
    )

    # =========================
    # 🔥 TOTAL STATS
    # =========================
    totals = daily_entries.aggregate(
        total_matches=Count("id", filter=Q(day_type="match")),
        total_training_days=Count("id", filter=Q(day_type="training")),

        total_minutes=Sum("minutes_played"),
        total_training_minutes=Sum("training_minutes"),

        total_goals=Sum("goals"),
        total_assists=Sum("assists"),
        total_pre_assists=Sum("pre_assists"),

        total_yellow=Sum("yellow_cards"),
        total_red=Sum("red_cards"),

        total_clean_sheets=Count("id", filter=Q(clean_sheet=True)),
    )

    # =========================
    # 🔥 APPEARANCE STATS
    # =========================
    appearances = daily_entries.aggregate(
        appearances=Count("id", filter=Q(appearance=True)),
        starts=Count("id", filter=Q(started=True)),
    )

    # =========================
    # 🔥 PERFORMANCE METRICS
    # =========================
    performance = daily_entries.aggregate(
        avg_minutes=Avg("minutes_played"),
        avg_training_minutes=Avg("training_minutes"),
    )

    # =========================
    # 🔥 EFFICIENCY METRICS
    # =========================
    matches = totals["total_matches"] or 0
    goals = totals["total_goals"] or 0
    assists = totals["total_assists"] or 0

    efficiency = {
        "goals_per_match": round(goals / matches, 2) if matches else 0,
        "assists_per_match": round(assists / matches, 2) if matches else 0,
        "goal_contribution": round((goals + assists) / matches, 2) if matches else 0,
    }

    # =========================
    # 🔥 RECENT FORM (LAST 5)
    # =========================
    recent_entries = daily_entries[:5]

    # =========================
    # 🔥 CONTEXT
    # =========================
    context = {
        "player": player,
        "daily_entries": daily_entries,

        # stats
        "totals": totals,
        "appearances": appearances,
        "performance": performance,
        "efficiency": efficiency,

        # extra
        "recent_entries": recent_entries,
    }

    return render(request, "loans_app_v2/loan_player_details.html", context)