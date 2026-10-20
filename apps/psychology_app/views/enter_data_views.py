from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from version1.players_app.models import Player
from ..forms import AssessmentForm
from ..models import Assessment


@staff_member_required
def assessment_list(request):
    assessments = Assessment.objects.select_related(
        'player', 'player__team', 'player__age_group'
    )

    return render(
        request,
        'psychology_app/assessment_list.html',
        {'assessments': assessments},
    )


@staff_member_required
def add_assessment(request):
    if request.method == 'POST':
        form = AssessmentForm(request.POST)

        if form.is_valid():
            assessment = form.save()
            messages.success(
                request,
                f'Assessment for {assessment.player.full_name} saved successfully.'
            )
            return redirect('psychology_app:assessment_list')
    else:
        form = AssessmentForm()

    return render(
        request,
        'psychology_app/add_assessment.html',
        {'form': form},
    )


@staff_member_required
def filter_players(request):
    players = Player.objects.filter(is_active=True).select_related(
        'team', 'age_group'
    )

    age_group_id = request.GET.get('age_group')
    team_id = request.GET.get('team')

    if age_group_id:
        players = players.filter(age_group_id=age_group_id)

    if team_id:
        players = players.filter(team_id=team_id)

    players = players.order_by('name', 'second_name', 'surname')

    return JsonResponse({
        'players': [
            {'id': player.pk, 'name': player.full_name}
            for player in players
        ]
    })


@staff_member_required
def assessment_detail(request, pk):
    assessment = get_object_or_404(
        Assessment.objects.select_related('player'),
        pk=pk,
    )

    return render(
        request,
        'psychology_app/assessment_detail.html',
        {'assessment': assessment},
    )