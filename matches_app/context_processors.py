from matches_app.models import Competition

def competitions_processor(request):
    
    return {
        "competition_choices": Competition.objects.all()
    }
