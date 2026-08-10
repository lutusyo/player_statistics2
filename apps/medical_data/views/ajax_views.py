from django.http import JsonResponse
from version1.players_app.models import Player
from version1.teams_app.models import Team

from django.http import JsonResponse
from version1.players_app.models import Player


def load_players(request):
    team_id = request.GET.get("team")

    players = (
        Player.objects
        .filter(team_id=team_id)
        .order_by("name", "second_name", "surname")
    )

    data = [
        {
            "id": player.id,
            "name": " ".join(
                filter(
                    None,
                    [
                        player.name,
                        player.second_name,
                        player.surname,
                    ],
                )
            ),
        }
        for player in players
    ]

    return JsonResponse(data, safe=False)