from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from weasyprint import HTML
from io import BytesIO
import base64
import matplotlib.pyplot as plt

from matches_app.models import Match
from gps_app.models import GPSRecord
from lineup_app.models import MatchLineup


def gps_pdf_export(request, match_id):
    match = get_object_or_404(Match, id=match_id)

    # Only include Session data
    gps_records = GPSRecord.objects.filter(
        match=match,
        period_name='Session'
    ).select_related('player')

    # 🔹 Minutes played lookup (player_id → minutes)
    minutes_map = {
        ml.player_id: ml.minutes_played
        for ml in MatchLineup.objects.filter(match=match)
    }

    gps_data = []
    for r in gps_records:
        gps_data.append({
            'player': r.player.name,
            'minutes': minutes_map.get(r.player_id, 0),  # ✅ ADDED
            'position': getattr(r.player, 'position', 'N/A'),
            'distance': r.distance or 0,
            'accel_decel': r.accel_decel_efforts or 0,
            'sprint_efforts': r.sprint_efforts or 0,
            'high_speed': r.high_speed_efforts or 0,
            'walking_distance': r.walking_distance or 0,
            'jogging_distance': r.jogging_distance or 0,
            'running_distance': r.running_distance or 0,
            'high_speed_distance': r.high_speed_distance or 0,
            'sprint_distance': r.sprint_distance or 0,
        })

    chart_images = []

    # ---------- BAR CHART ----------
    def generate_bar_chart(labels, values, title, ylabel, color='skyblue'):
        plt.figure(figsize=(8, 4))
        plt.bar(labels, values, color=color, edgecolor='black')
        plt.title(title, fontsize=14, color='darkblue')
        plt.xticks(rotation=45, ha='right')
        plt.ylabel(ylabel, fontsize=12, color='darkred')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()

        buf = BytesIO()
        plt.savefig(buf, format='png', facecolor='white')
        buf.seek(0)
        img_base64 = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
        buf.close()
        plt.close()
        return img_base64

    players = [r['player'] for r in gps_data]

    distances = [r['distance'] for r in gps_data]
    chart_images.append(
        generate_bar_chart(players, distances, 'Distance per Player', 'Distance (m)')
    )

    # ---------- RADAR CHART ----------
    def generate_radar_chart(values, labels, title, color='#1f77b4'):
        N = len(values)
        angles = [n / float(N) * 2 * 3.14159265 for n in range(N)]
        values = values + values[:1]
        angles = angles + angles[:1]

        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        ax.plot(angles, values, color=color, linewidth=2)
        ax.fill(angles, values, color=color, alpha=0.25)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels, rotation=45, fontsize=10)
        ax.set_title(title, fontsize=14, y=1.1, color='darkgreen')
        ax.set_yticks([])
        plt.tight_layout()

        buf = BytesIO()
        plt.savefig(buf, format='png', facecolor='white')
        buf.seek(0)
        img_base64 = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
        buf.close()
        plt.close()
        return img_base64

    radar_fields = [
        ('Accel/Decel Efforts', 'accel_decel'),
        ('Sprint Efforts', 'sprint_efforts'),
        ('High Speed Efforts', 'high_speed'),
        ('Walking Distance', 'walking_distance'),
        ('Jogging Distance', 'jogging_distance'),
        ('Running Distance', 'running_distance'),
        ('High Speed Distance', 'high_speed_distance'),
        ('Sprint Distance', 'sprint_distance'),
    ]

    for title, field in radar_fields:
        values = [r[field] for r in gps_data]
        chart_images.append(generate_radar_chart(values, players, title))

    # ---------- RENDER PDF ----------
    html_string = render_to_string(
        'gps_app/gps_dashboard_pdf.html',
        {
            'match': match,
            'gps_data': gps_data,
            'chart_images': chart_images,
        }
    )

    pdf_file = HTML(string=html_string).write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'filename="gps_dashboard_{match.id}.pdf"'
    return response
