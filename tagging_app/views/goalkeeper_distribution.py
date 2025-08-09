from django.shortcuts import render, get_object_or_404
from players_app.models import Player
from matches_app.models import Match, MatchLineup
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from collections import defaultdict
from django.db.models import Count
import traceback
from tagging_app.models import  GoalkeeperDistributionEvent
from teams_app.models import Team

from django.http import FileResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.http import HttpResponse
import io


def goalkeeper_distribution_page(request, match_id):
    match = get_object_or_404(Match, id=match_id)

    # Filter all players who are goalkeepers
    gk_players = MatchLineup.objects.filter(
        match=match,
        position='GK'
    ).select_related('player', 'team')

    context = {
        'match': match,
        'goalkeepers': gk_players,
    }
    return render(request, 'tagging_app/goalkeeper_distribution_enter_data.html', context)

@csrf_exempt
def save_goalkeeper_distribution(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            GoalkeeperDistributionEvent.objects.create(
                match=Match.objects.get(id=data['match_id']),
                goalkeeper=Player.objects.get(id=data['goalkeeper_id']),
                team=Team.objects.get(id=data['team_id']),
                minute=data['minute'],
                second=data['second'],
                method=data['method'],
                detail=data['detail'],
                is_complete=data['is_complete'],
                is_goal_conceded=data.get('is_goal_conceded', False),
                involvement_duration=data.get('involvement_duration')
            )
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'invalid'})

def goalkeeper_distribution_dashboard(request, match_id):
    # Get match info
    match = get_object_or_404(Match, id=match_id)
    
    # Get goalkeeper distribution data for this match
    distributions = GoalkeeperDistributionEvent.objects.filter(match=match)
    
    context = {
        'match': match,
        'distributions': distributions,
    }
    return render(request, 'tagging_app/goalkeeper_distribution_dashboard.html', context)



def export_goalkeeper_distribution_csv(request, match_id):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="gk_distribution_{match_id}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Goalkeeper', 'Distribution Type', 'Target Player'])

    distributions = GoalkeeperDistributionEvent.objects.filter(match_id=match_id)
    for d in distributions:
        writer.writerow([d.goalkeeper.name, d.distribution_type, d.target_player.name])
    return response



def export_goalkeeper_distribution_pdf(request, match_id):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    c.drawString(100, 800, f"Goalkeeper Distribution Report for Match {match_id}")
    
    events = GoalkeeperDistributionEvent.objects.filter(match_id=match_id)
    y = 750
    for e in events:
        c.drawString(100, y, f"{e.goalkeeper.name} - {e.distribution_type} ➡ {e.target_player.name}")
        y -= 15
        if y < 50:
            c.showPage()
            y = 800

    c.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='goalkeeper_distribution.pdf')

