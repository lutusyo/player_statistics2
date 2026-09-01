from django.contrib import messages
from django.shortcuts import render, redirect
from version2.psychology_app_v2.forms import AssessmentForm

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect

from version1.players_app.models import Player
from version2.psychology_app_v2.forms import AssessmentForm
from version2.psychology_app_v2.models import Assessment


def add_assessment(request):

    if request.method == 'POST':

        form = AssessmentForm(request.POST)

        if form.is_valid():

            assessment = form.save()

            messages.success(
                request,
                f"Assessment for {assessment.player.full_name} saved successfully."
            )

            return redirect('psychology_app_v2:assessment_history')

    else:
        form = AssessmentForm()

    return render(
        request,
        'psychology_app_v2/add_assessment.html',
        {
            'form': form,
        }
    )


def filter_players(request):

    age_group_id = request.GET.get('age_group')
    team_id = request.GET.get('team')

    players = Player.objects.filter(
        is_active=True
    ).select_related(
        'team',
        'age_group'
    )

    if age_group_id:
        players = players.filter(
            age_group_id=age_group_id
        )

    if team_id:
        players = players.filter(
            team_id=team_id
        )

    players = players.order_by(
        'name',
        'second_name',
        'surname'
    )

    data = []

    for player in players:

        data.append({
            'id': player.id,
            'name': player.full_name,
        })

    return JsonResponse({
        'players': data
    })