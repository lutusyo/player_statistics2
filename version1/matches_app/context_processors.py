# matches_app/context_processors.py

from version1.matches_app.models import Competition
from .models import CompetitionSeason

def competitions_processor(request):
    
    return {
        "competition_choices": Competition.objects.all()
    }



def competition_seasons(request):
    return {
        "competition_seasons": CompetitionSeason.objects.all()
    }