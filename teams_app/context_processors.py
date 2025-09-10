# teams_app/context_processors.py

from .models import Team

def our_teams_context(request):
    our_teams = Team.objects.filter(team_type='OUR_TEAM').select_related('age_group')
    return {'our_teams': our_teams}
