# perfomance_rating_app/views.py

from django.shortcuts import render
from players_app.models import Player
from perfomance_rating_app.models import PerformanceRating

def season_player_overview(request, season):
    """
    Aggregated season ratings for ALL players, sorted by highest average rating.
    Works with the template player_season_overview.html
    """

    all_players = Player.objects.all()

    players_data = []

    for player in all_players:

        ratings = PerformanceRating.objects.filter(
            player=player,
            match__season=season,
            is_computed=True
        )

        count = ratings.count()
        if count == 0:
            continue  # skip players with no data

        total_att = sum(r.attacking or 0 for r in ratings)
        total_cre = sum(r.creativity or 0 for r in ratings)
        total_def = sum(r.defending or 0 for r in ratings)
        total_tac = sum(r.tactical or 0 for r in ratings)
        total_tec = sum(r.technical or 0 for r in ratings)

        # Averages
        avg_att = round(total_att / count, 2)
        avg_cre = round(total_cre / count, 2)
        avg_def = round(total_def / count, 2)
        avg_tac = round(total_tac / count, 2)
        avg_tec = round(total_tec / count, 2)

        overall_avg = round(
            (avg_att + avg_cre + avg_def + avg_tac + avg_tec) / 5, 2
        )

        players_data.append({
            "player": player,
            "attacking": avg_att,
            "creativity": avg_cre,
            "defending": avg_def,
            "tactical": avg_tac,
            "technical": avg_tec,
            "average": overall_avg,
            "count": count
        })

    # Sort by highest overall rating
    players_data = sorted(players_data, key=lambda x: x["average"], reverse=True)

    return render(request, "performance_rating_app/player_season_overview.html", {
        "season": season,
        "players": players_data,
    })
