from django.shortcuts import render

from version1.players_app.models import Player
from version1.teams_app.models import AgeGroup, Team
from version2.psychology_app_v2.models import Assessment


def assessment_history(request):

    age_group_id = request.GET.get('age_group')
    team_id = request.GET.get('team')
    player_id = request.GET.get('player')

    assessments = Assessment.objects.select_related(
        'player',
        'player__team',
        'player__age_group'
    ).all()


    if age_group_id:

        assessments = assessments.filter(
            player__age_group_id=age_group_id
        )


    if team_id:

        assessments = assessments.filter(
            player__team_id=team_id
        )


    if player_id:

        assessments = assessments.filter(
            player_id=player_id
        )


    age_groups = AgeGroup.objects.all().order_by('name')

    teams = Team.objects.all().order_by('name')

    players = Player.objects.filter(
        is_active=True
    ).order_by(
        'name',
        'second_name',
        'surname'
    )


    context = {

        'assessments': assessments,

        'age_groups': age_groups,

        'teams': teams,

        'players': players,

        'selected_age_group': age_group_id,

        'selected_team': team_id,

        'selected_player': player_id,
    }


    return render(
        request,
        'psychology_app_v2/assessment_history.html',
        context
    )