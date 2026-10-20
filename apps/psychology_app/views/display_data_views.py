
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Avg, Count, Q
from django.shortcuts import render, get_object_or_404

from version1.players_app.models import Player
from ..models import Assessment


@staff_member_required
def dashboard(request):
    assessments = Assessment.objects.select_related('player')

    context = {
        'total_players': Player.objects.filter(is_active=True).count(),
        'assessed_players': assessments.values('player_id').distinct().count(),
        'total_assessments': assessments.count(),
        'average_score': assessments.aggregate(
            average=Avg('overall')
        )['average'],
        'recent_assessments': assessments.order_by('-created_at')[:8],
    }

    return render(request, 'psychology_app/dashboard.html', context)


@staff_member_required
def player_directory(request):
    players = Player.objects.filter(is_active=True).select_related(
        'team', 'age_group'
    )

    search = request.GET.get('q', '').strip()
    team_id = request.GET.get('team', '')
    age_group_id = request.GET.get('age_group', '')

    if search:
        players = players.filter(
            Q(name__icontains=search)
            | Q(second_name__icontains=search)
            | Q(surname__icontains=search)
        )

    if team_id:
        players = players.filter(team_id=team_id)

    if age_group_id:
        players = players.filter(age_group_id=age_group_id)

    players = players.annotate(
        assessment_count=Count('psychology_app_assessments')
    ).order_by('name', 'second_name', 'surname')

    from version1.teams_app.models import AgeGroup, Team

    context = {
        'players': players,
        'teams': Team.objects.all().order_by('name'),
        'age_groups': AgeGroup.objects.all().order_by('name'),
        'search': search,
        'selected_team': team_id,
        'selected_age_group': age_group_id,
    }

    return render(request, 'psychology_app/player_directory.html', context)


@staff_member_required
def player_profile(request, player_id):
    player = get_object_or_404(
        Player.objects.select_related('team', 'age_group'),
        pk=player_id,
    )

    assessments = player.psychology_app_assessments.all()

    context = {
        'player': player,
        'assessments': assessments,
        'total_assessments': assessments.count(),
        'latest_assessment': assessments.first(),
        'average_score': assessments.aggregate(
            average=Avg('overall')
        )['average'],
    }

    return render(
        request,
        'psychology_app/player_profile.html',
        context,
    )
