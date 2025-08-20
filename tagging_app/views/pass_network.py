# tagging_app/views/pass_network.py
from django.shortcuts import render, get_object_or_404
from players_app.models import Player
from matches_app.models import Match
from lineup_app.models import MatchLineup
from django.utils import timezone
from django.http import JsonResponse, HttpResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
import json
from collections import defaultdict
from django.db.models import Count, Avg
from tagging_app.models import PassEvent, GoalkeeperDistributionEvent
from teams_app.models import Team
import csv
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from tagging_app.views.goal_and_pass_enter import tagging_base_view




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

            # Save pass
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

            # Get updated count of passes from this player in this match
            count = PassEvent.objects.filter(match=match, from_player=from_player).count()

            return JsonResponse({'status': 'success', 'count': count})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'invalid request'})


def pass_network_dashboard(request, match_id):
    match = get_object_or_404(Match, id=match_id)

    # Get all player IDs involved in passes for this match (from and to)
    player_ids_from = PassEvent.objects.filter(match=match).values_list('from_player_id', flat=True)
    player_ids_to = PassEvent.objects.filter(match=match).values_list('to_player_id', flat=True)
    all_player_ids = set(player_ids_from).union(set(player_ids_to))

    players = Player.objects.filter(id__in=all_player_ids)
    player_names = {p.id: p.name for p in players}

    # Matrix: {from_id: {to_id: count}}
    matrix = defaultdict(lambda: defaultdict(int))
    passes = PassEvent.objects.filter(match=match).values('from_player_id', 'to_player_id').annotate(count=Count('id'))

    for p in passes:
        if p['to_player_id']:
            matrix[p['from_player_id']][p['to_player_id']] = p['count']

    # Top 5 combinations (safe get to avoid KeyError)
    top_combinations = sorted(
        [
            (player_names.get(f, f"Unknown ({f})"), player_names.get(t, f"Unknown ({t})"), c)
            for f, tos in matrix.items() for t, c in tos.items()
        ],
        key=lambda x: x[2], reverse=True
    )[:5]

    context = {
        'match': match,
        'players': players,
        'matrix': matrix,
        'player_names': player_names,
        'top_combinations': top_combinations,
    }
    return render(request, 'tagging_app/pass_network_dashboard.html', context)


def export_pass_network_csv(request, match_id):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="pass_events_match_{match_id}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Match', 'From', 'To', 'Minute', 'Second', 'X Start', 'Y Start', 'X End', 'Y End'])

    passes = PassEvent.objects.filter(match_id=match_id).select_related('match', 'from_player', 'to_player')

    for event in passes:
        writer.writerow([
            str(event.match),
            event.from_player.name,
            event.to_player.name if event.to_player else 'Loss',
            event.minute,
            event.second,
            event.x_start,
            event.y_start,
            event.x_end,
            event.y_end
        ])

    return response


def export_pass_network_excel(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    wb = Workbook()
    ws = wb.active
    ws.title = "Pass Network Matrix"

    # Get all player IDs involved in passes for this match
    player_ids_from = PassEvent.objects.filter(match=match).values_list('from_player_id', flat=True)
    player_ids_to = PassEvent.objects.filter(match=match).values_list('to_player_id', flat=True)
    all_player_ids = set(player_ids_from).union(set(player_ids_to))

    players = Player.objects.filter(id__in=all_player_ids)
    player_names = {p.id: p.name for p in players}

    matrix = defaultdict(lambda: defaultdict(int))
    passes = PassEvent.objects.filter(match=match).values('from_player_id', 'to_player_id').annotate(count=Count('id'))
    for p in passes:
        if p['to_player_id']:
            matrix[p['from_player_id']][p['to_player_id']] = p['count']

    ws.cell(row=1, column=1, value="From\\To")
    for col_index, p in enumerate(players, start=2):
        ws.cell(row=1, column=col_index, value=player_names[p.id][:10])

    for row_index, from_player in enumerate(players, start=2):
        ws.cell(row=row_index, column=1, value=player_names[from_player.id][:10])
        for col_index, to_player in enumerate(players, start=2):
            if from_player.id == to_player.id:
                ws.cell(row=row_index, column=col_index, value="—")
            else:
                ws.cell(row=row_index, column=col_index, value=matrix[from_player.id].get(to_player.id, 0))

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="pass_network_{match_id}.xlsx"'
    wb.save(response)
    return response


def export_pass_network_pdf(request, match_id):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    match = get_object_or_404(Match, id=match_id)

    # Get all player IDs involved in passes for this match
    player_ids_from = PassEvent.objects.filter(match=match).values_list('from_player_id', flat=True)
    player_ids_to = PassEvent.objects.filter(match=match).values_list('to_player_id', flat=True)
    all_player_ids = set(player_ids_from).union(set(player_ids_to))

    players = Player.objects.filter(id__in=all_player_ids)
    player_names = {p.id: p.name for p in players}

    # Matrix
    matrix = defaultdict(lambda: defaultdict(int))
    passes = PassEvent.objects.filter(match=match).values('from_player_id', 'to_player_id').annotate(count=Count('id'))

    for p in passes:
        if p['to_player_id']:
            matrix[p['from_player_id']][p['to_player_id']] = p['count']

    data = [["From\\To"] + [player_names[p.id][:10] for p in players]]
    for row_player in players:
        row = [player_names[row_player.id][:10]]
        for col_player in players:
            if row_player.id == col_player.id:
                row.append("—")
            else:
                row.append(str(matrix[row_player.id].get(col_player.id, 0)))
        data.append(row)

    t = Table(data)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    ]))
    elements.append(Paragraph(f"Passing Network Matrix - {match}", styles['Title']))
    elements.append(t)

    doc.build(elements)
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='pass_network_matrix.pdf')
