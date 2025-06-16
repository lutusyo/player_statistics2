from django.shortcuts import render, get_object_or_404
from .models import Player, PlayerCareerStage
from django.db.models import Sum, Count
from django.contrib.auth.decorators import login_required
from collections import defaultdict



@login_required
def player_list(request):
    age_group = request.GET.get('age_group')

    if age_group:
        players = Player.objects.filter(age_group=age_group)
    else:
        players = Player.objects.filter(age_group='U20')

    # Group players by position
    grouped_players = defaultdict(list)
    for player in players:
        grouped_players[player.position].append(player)

    # Define the order in which positions should appear
    position_order = ['Goalkeeper', 'Defender', 'Midfielder', 'Forward']

    # Get distinct age groups for the filter dropdown
    age_groups = Player.objects.values_list('age_group', flat=True).distinct()

    return render(request, 'players_app/player_list.html', {
        'grouped_players': grouped_players,
        'position_order': position_order,
        'players': players,
        'age_groups': age_groups,
        'selected_age_group': age_group
    })


@login_required
def player_detail(request, player_id):
    player = get_object_or_404(Player, id=player_id)
    stages = player.career_stages.all()
    return render(request, 'players_app/player_detail.html', {'player': player, 'stages': stages})