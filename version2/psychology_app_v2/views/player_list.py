import pandas as pd
from django.shortcuts import render
from version2.psychology_app_v2.forms import UploadExcelForm
from version2.psychology_app_v2.models import Player, Assessment, AgeGroup


from django.db.models import Avg
from django.shortcuts import get_object_or_404
import json



def player_list(request):
    age_group_id = request.GET.get('age_group')

    players = Player.objects.prefetch_related('assessments')

    if age_group_id:
        players = players.filter(age_group_id=age_group_id)

    age_groups = AgeGroup.objects.all()

    context = {
        'players': players,
        'age_groups': age_groups,
        'selected_age_group': age_group_id,
    }

    return render(request, 'psychology_app_v2/player_list.html', context)



