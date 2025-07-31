from django.shortcuts import render, get_object_or_404
from .models import Player, PlayerCareerStage
from django.db.models import Sum, Count
from django.contrib.auth.decorators import login_required
from collections import defaultdict
from django.http import Http404

from teams_app.models import AgeGroup

@login_required
def player_list(request):
    age_group_code = request.GET.get('age_group')

    if age_group_code:
        try:
            age_group = AgeGroup.objects.get(code=age_group_code)
            players = Player.objects.filter(age_group=age_group, is_active=True)
        except AgeGroup.DoesNotExist:
            players = Player.objects.none()
    else:
        players = Player.objects.filter(age_group__code='U20', is_active=True)

    # Group players by position
    grouped_players = defaultdict(list)
    for player in players:
        grouped_players[player.position].append(player)

    position_order = ['Goalkeeper', 'Defender', 'Midfielder', 'Forward']

    age_groups = AgeGroup.objects.values_list('code', flat=True)

    return render(request, 'players_app/player_list.html', {
        'grouped_players': grouped_players,
        'position_order': position_order,
        'players': players,
        'age_groups': age_groups,
        'selected_age_group': age_group_code
    })

@login_required
def player_detail(request, player_id):
    player = get_object_or_404(Player, id=player_id)

    # 🔒 Prevent showing detail of inactive player
    if not player.is_active:
        raise Http404("This player is inactive")

    # Only show active related players
    related_players = Player.objects.filter(
        age_group=player.age_group,
        is_active=True
    ).exclude(id=player_id)

    stages = player.career_stages.all()
    selected_age_group = request.GET.get('age_group')

    context = {
        'player': player,
        'related_players': related_players,
        'stages': stages,
        'selected_age_group': selected_age_group,
    }
    return render(request, 'players_app/player_detail.html', context)
