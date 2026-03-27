from django.shortcuts import render, get_object_or_404
from django.db.models import Sum, Avg, Count
from django.contrib.auth.decorators import login_required
from collections import defaultdict
from django.http import Http404

from version1.teams_app.models import AgeGroup
from version1.matches_app.models import Match
from version1.lineup_app.models import MatchLineup
from version1.gps_app.models import GPSRecord
from version1.tagging_app.models import AttemptToGoal, PassEvent, GoalkeeperDistributionEvent

#from goalkeeping_app.models import GoalkeeperDistributionEvent
from version1.defensive_app.models import PlayerDefensiveStats
from version1.players_app.models import Player, PlayerCareerStage

@login_required
def player_list(request):
    age_group_code = request.GET.get('age_group')

    players = Player.objects.filter(is_active=True)

    if age_group_code:
        try:
            age_group = AgeGroup.objects.get(code=age_group_code)
            players = players.filter(age_group=age_group)
        except AgeGroup.DoesNotExist:
            players = Player.objects.none()
    else:
        players = players.filter(age_group__code='U20')

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
