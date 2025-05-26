from django.shortcuts import render, get_object_or_404
from .models import Player

def player_list(request):
    players = Player.objects.all()
    return render(request, 'stats/profile/player_list.html', {'players': players})


def player_detail(request, player_id):
    player = get_object_or_404(Player, id=player_id)
    return render(request, 'stats/profile/player_detail.html', {'player': player})
