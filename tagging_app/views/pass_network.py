# tagging_app/views/pass_network.py
from django.shortcuts import render, get_object_or_404
from players_app.models import Player
from matches_app.models import Match, MatchLineup
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from collections import defaultdict
from django.db.models import Count, Avg
import traceback

from tagging_app.models import PassEvent, GoalkeeperDistributionEvent
from teams_app.models import Team

import csv
from django.http import HttpResponse

from django.http import FileResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def pass_network_page(request, match_id):
    match = get_object_or_404(Match, id=match_id)

    our_team = match.home_team  # or logic to detect viewer's team
    opponent_team = match.away_team

    our_players = MatchLineup.objects.filter(match=match, team=our_team, is_starting=True)
    opponent_players = MatchLineup.objects.filter(match=match, team=opponent_team, is_starting=True)

    context = {
        'match': match,
        'our_team': our_team,
        'opponent_team': opponent_team,
        'our_players': our_players,
        'opponent_players': opponent_players,
    }
    return render(request, 'tagging_app/pass_network_enter_data.html', context)



@csrf_exempt
def save_pass_network(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            match = Match.objects.get(id=data['match_id'])
            from_player = Player.objects.get(id=data['from_player_id'])
            to_player = Player.objects.get(id=data.get('to_player_id')) if data.get('to_player_id') else None
            from_team = Team.objects.get(id=data['from_team_id'])
            to_team = Team.objects.get(id=data['to_team_id'])

            PassEvent.objects.create(
                match=match,
                from_player=from_player,
                to_player=to_player,
                from_team=from_team,
                to_team=to_team,
                minute=data['minute'],
                second=data['second'],
                x_start=data.get('x_start'),
                y_start=data.get('y_start'),
                x_end=data.get('x_end'),
                y_end=data.get('y_end'),
                is_successful=data['is_successful'],
                is_possession_regained=data.get('is_possession_regained', False)
            )
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'invalid request'})

def pass_network_dashboard(request):
    # Example GK stats
    gk_stats = GoalkeeperDistributionEvent.objects.values('gk_player__name').annotate(
        saves=Count('save'),
        punches=Count('punch'),
        catches=Count('catch'),
        avg_position_x=Avg('position_x'),
        avg_position_y=Avg('position_y')
    )

    # Pass network data (top 10)
    pass_network = PassEvent.objects.values('from_player__name', 'to_player__name').annotate(
        count=Count('id')
    ).order_by('-count')[:10]

    return render(request, 'pass_event/dashboard.html', {
        'gk_stats': gk_stats,
        'pass_network': pass_network,
    })

def export_pass_network_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="pass_events.csv"'

    writer = csv.writer(response)
    writer.writerow(['Match', 'From', 'To', 'Minute', 'X', 'Y'])

    for event in PassEvent.objects.select_related('match', 'from_player', 'to_player'):
        writer.writerow([
            event.match,
            event.from_player.name,
            event.to_player.name,
            event.minute,
            event.position_x,
            event.position_y
        ])
    return response


def export_pass_network_pdf(request, match_id):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    c.drawString(100, 800, f"Pass Network Report for Match {match_id}")
    
    passes = PassEvent.objects.filter(match_id=match_id)
    y = 750
    for p in passes:
        c.drawString(100, y, f"{p.player.name} ➡ {p.receiver.name} | Zone: {p.zone_x}, {p.zone_y}")
        y -= 15
        if y < 50:
            c.showPage()
            y = 800

    c.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='pass_network.pdf')
