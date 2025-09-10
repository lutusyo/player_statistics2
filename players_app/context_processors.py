from .models import Player

def player_filters(request):
    age_groups = Player.objects.values_list('age_group', flat=True).distinct()
    selected_age_group = request.GET.get('age_group', '')
    return {
        'age_groups': age_groups,
        'selected_age_group': selected_age_group,
    }
