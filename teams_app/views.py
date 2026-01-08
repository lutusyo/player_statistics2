from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from players_app.models import Player
from collections import defaultdict
from .models import StaffMember
from teams_app.models import Team

@login_required
def team_squad_view(request, pk):
    team = Team.objects.filter(
        id=pk,
        team_type='OUR_TEAM'
    ).select_related('age_group').first()

    if not team:
        return render(request, '404.html', status=404)

    # ✅ ONLY ACTIVE PLAYERS
    players = Player.objects.filter(
        team__team_type='OUR_TEAM',
        age_group=team.age_group,
        is_active=True
    ).select_related('team')

    grouped_players = defaultdict(list)
    for player in players:
        grouped_players[player.position].append(player)

    position_order = ['Goalkeeper', 'Defender', 'Midfielder', 'Winger', 'Forward']

    return render(request, 'teams_app/squad.html', {
        'team_selected': team,
        'grouped_players': grouped_players,
        'position_order': position_order,
        'active_tab': 'squad',
        'team': team,
    })




@login_required
def team_table(request, pk):
    team = Team.objects.filter(id=pk, team_type='OUR_TEAM').first()
    if not team:
        return render(request, '404.html', status=404)
    return render(request, 'teams_app/table.html', {
        'team_selected': team,
        'active_tab': 'table'
    })

@login_required
def team_honour(request, pk):
    team = Team.objects.filter(id=pk, team_type='OUR_TEAM').first()
    if not team:
        return render(request, '404.html', status=404)
    return render(request, 'teams_app/honour.html', {
        'team_selected': team,
        'active_tab': 'honour'
    })

@login_required
def team_statistics(request, pk):
    team = Team.objects.filter(id=pk, team_type='OUR_TEAM').first()
    if not team:
        return render(request, '404.html', status=404)
    return render(request, 'teams_app/statistics.html', {
        'team_selected': team,
        'active_tab': 'statistics'
    })



def staff_list(request):
    staff_members = StaffMember.objects.all().order_by('age_group', 'role')
    return render(request, 'teams_app/staff_list.html', {'staff_members': staff_members})
