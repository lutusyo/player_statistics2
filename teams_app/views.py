from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from players_app.models import Player
from collections import defaultdict
from .models import staffMember

@login_required
def team_squad(request, team):

    # Get players for the given team (age_group)
    players = Player.objects.filter(age_group=team)

    # Group players by position
    grouped_players = defaultdict(list)
    for player in players:
        grouped_players[player.position].append(player)

    # Define the order in which the position will appear
    position_order = ['Goalkeeper', 'Defender', 'Midfielder', 'Forward']

    return render(request, 'teams_app/squad.html', {
        'team_selected': team,
        'grouped_players': grouped_players,
        'position_order': position_order,
        'active_tab': 'squad',
    })

@login_required
def team_table(request, team):
    return render(request, 'teams_app/table.html', {
        'team_selected': team,
        'active_tab': 'table'
    })

@login_required
def team_honour(request, team):
    return render(request, 'teams_app/honour.html', {
        'team_selected': team,
        'active_tab': 'honour'
    })

@login_required
def team_statistics(request, team):
    return render(request, 'teams_app/statistics.html', {
        'team_selected': team,
        'active_tab': 'statistics'
    })


def staff_list(request):
    staff_members = staffMember.objects.all().order_by('age_group', 'role')
    return render(request, 'teams_app/staff_list.html', {'staff_members': staff_members})
