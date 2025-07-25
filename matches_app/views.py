from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from .models import Match, Goal, PlayerMatchStats, TeamMatchResult
from players_app.models import PlayerCareerStage, Player
from django.db.models import Sum, Count
from django.contrib.auth.decorators import login_required
from datetime import date
from gps_app.models import GPSRecord
from actions_app.models import PlayerDetailedAction
import csv
from django.http import HttpResponse
from .models import Match, PlayerMatchStats
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
import os
from actions_app.models import TeamActionStats, PlayerDetailedAction
from datetime import date, timedelta
from django.utils.timezone import now
from .models import Match, PlayerMatchStats, Goal

import calendar
from PIL import Image
from datetime import date
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from django.db.models import Sum

from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageTemplate, Frame)






def create_transparent_image(input_path, output_path, opacity=0.01):
    image = Image.open(input_path).convert("RGBA")
    alpha = image.split()[3]  # Get alpha channel
    alpha = alpha.point(lambda p: int(p * opacity))  # Apply opacity
    image.putalpha(alpha)
    image.save(output_path, format='PNG')


@login_required
def team_dashboard(request, team):
    # Just redirect to the fixtures view
    return redirect('matches_app:team_fixtures', team=team)


@login_required
def player_statistics_view(request, team):
    selected_season = request.GET.get('season')
    selected_age_group = request.GET.get('age_group')
    selected_competition = request.GET.get('competition')

    matches = Match.objects.all()
    seasons = dict(Match._meta.get_field('season').choices)
    competitions = dict(Match._meta.get_field('competition_type').choices)
    age_groups = dict(Player._meta.get_field('age_group').choices)

    stats = PlayerMatchStats.objects.select_related('player', 'match')
    players = Player.objects.filter(age_group=team)

    if selected_season:
        stats = stats.filter(match__season=selected_season)

    if selected_age_group:
        stats = stats.filter(player__age_group=selected_age_group)
        players = players.filter(age_group=selected_age_group)

    if selected_competition:
        stats = stats.filter(match__competition_type=selected_competition)

    player_data = []
    for player in players:
        player_stats = stats.filter(player=player)

        def get_stats_by_competition(comp):
            comp_stats = player_stats.filter(match__competition_type=comp)
            return {
                'appearances': comp_stats.count(),
                'goals': Goal.objects.filter(
                    match__in=comp_stats.values('match'),
                    scorer=player,
                    is_own_goal=False
                ).count()
            }

        local = get_stats_by_competition('Local Friendly')
        international = get_stats_by_competition('International Friendly')
        nbc = get_stats_by_competition('NBC Youth League')

        player_info = {
            'player': player,
            'local_ap': local['appearances'],
            'local_gl': local['goals'],
            'int_ap': international['appearances'],
            'int_gl': international['goals'],
            'nbc_ap': nbc['appearances'],
            'nbc_gl': nbc['goals'],
            'total_ap': local['appearances'] + international['appearances'] + nbc['appearances'],
            'total_gl': local['goals'] + international['goals'] + nbc['goals'],
        }

        # Only include goalkeeper stats if the player is a goalkeeper
        if player.position == 'Goalkeeper':
            player_info.update({
                'saves_success_rate': round(player_stats.aggregate(Sum('saves_success_rate'))['saves_success_rate__sum'] or 0, 2),
                'clean_sheets': player_stats.aggregate(Sum('clean_sheets'))['clean_sheets__sum'] or 0,
                'catches': player_stats.aggregate(Sum('catches'))['catches__sum'] or 0,
                'punches': player_stats.aggregate(Sum('punches'))['punches__sum'] or 0,
                'drops': player_stats.aggregate(Sum('drops'))['drops__sum'] or 0,
                'penalties_saved': player_stats.aggregate(Sum('penalties_saved'))['penalties_saved__sum'] or 0,
                'clearances': player_stats.aggregate(Sum('clearances'))['clearances__sum'] or 0,

                # distribution
                'total_passes': player_stats.aggregate(Sum('total_passes'))['total_passes__sum'] or 0,
                'pass_success_rate': round(player_stats.aggregate(Sum('pass_success_rate'))['pass_success_rate__sum'] or 0, 2),
                'long_pass_success': round(player_stats.aggregate(Sum('long_pass_success'))['long_pass_success__sum'] or 0, 2),

                # discipline
                'fouls_won': player_stats.aggregate(Sum('fouls_won'))['fouls_won__sum'] or 0,
                'fouls_conceded': player_stats.aggregate(Sum('fouls_conceded'))['fouls_conceded__sum'] or 0,
                'yellow_cards': player_stats.aggregate(Sum('yellow_cards'))['yellow_cards__sum'] or 0,
                'red_cards': player_stats.aggregate(Sum('red_cards'))['red_cards__sum'] or 0,
            })

        player_data.append(player_info)

    context = {
        'seasons': seasons,
        'age_groups': age_groups,
        'competitions': competitions,
        'selected_season': selected_season,
        'selected_age_group': selected_age_group,
        'selected_competition': selected_competition,
        'player_data': player_data,
        'team_selected': team,

    }
    return render(request, 'matches_app/players_statistics.html', context)


@login_required
def career_stage_detail(request, stage_id):
    stage = get_object_or_404(PlayerCareerStage, id=stage_id)
    selected_age_group = request.GET.get('age_group')

    context = {
        'stage': stage,
        'selected_age_group': selected_age_group,

    }

    return render(request, 'matches_app/career_stage_detail.html', context)


@login_required
def fixtures_view(request, team):
    upcoming_matches = Match.objects.filter(team=team, date__gte=date.today()).order_by('date')
    past_matches = Match.objects.filter(team=team, date__lt=date.today()).order_by('-date')

    context = {
        'team': team,
        'upcoming_matches': upcoming_matches,
        'past_matches': past_matches,
        'team_selected': team,
        'active_tab': 'fixtures',
    }
    return render(request, 'matches_app/fixtures.html', context)


@login_required
def results_view(request, team):

    context = {
        "team": team,
        'team_selected': team,
        'active_tab': 'results',
    }
    return render(request, 'matches_app/match_results.html', context)


@login_required
def table_view(request, team):

    context = {
        'team': team,
        'team_selected': team,
        'active_tab': 'table',
    }
    return render(request, 'teams_app/table.html', context)


@login_required
def match_detail(request, match_id):
    match = get_object_or_404(Match, pk=match_id)
    player_stats = PlayerMatchStats.objects.filter(match=match).select_related('player')
    goals = Goal.objects.filter(match=match).select_related('scorer', 'assist_by')
    team_result = TeamMatchResult.objects.filter(match=match).first()
    team_stats = TeamActionStats.objects.filter(match=match).order_by('-is_our_team')

    team_str = str(match.team).strip()  # ensure it's a non-empty string

    return render(request, 'matches_app/match_details.html', {
        'match': match,
        'player_stats': player_stats,
        'goals': goals,
        'team_result': team_result,
        'team_stats': team_stats,
        'team_selected': team_str,
    })



def export_player_stats_csv(request, match_id):
    match = get_object_or_404(Match, pk=match_id)
    stats = PlayerMatchStats.objects.filter(match=match).select_related('player')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{match}-player-stats.csv"'

    writer = csv.writer(response)
    writer.writerow(['Player Name', 'Minutes Played', 'Goals', 'Assists', 'Yellow Cards', 'Red Cards'])

    for stat in stats:
        writer.writerow([
            stat.player.name,
            stat.minutes_played,
            stat.goals,
            stat.assists,
            stat.yellow_cards,
            stat.red_cards
        ])

    return response


def draw_background(p, logo_path, width, height):
    if os.path.exists(logo_path):
        try:
            p.saveState()
            p.drawImage(
                ImageReader(logo_path),
                0, 0,
                width=width,
                height=height,
                preserveAspectRatio=True,
                mask='auto'
            )
            p.restoreState()
        except Exception as e:
            print(f"Failed to draw background image: {e}")





def export_match_summary_pdf(request, match_id):
    match = get_object_or_404(Match, pk=match_id)
    stats = PlayerDetailedAction.objects.filter(match=match).select_related('player')
    player_match_stats = PlayerMatchStats.objects.filter(match=match).select_related('player')
    goals = Goal.objects.filter(match=match).select_related('scorer', 'assist_by')
    result = TeamMatchResult.objects.filter(match=match).first()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="match-summary-{match.id}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    width, height = A4

    # --- Match Summary Title and Info ---
    elements.append(Paragraph(f"<b>{match.get_team_display()} vs {match.opponent}</b>", styles['Title']))
    elements.append(Paragraph(f"Venue: {match.venue} | Date: {match.date.strftime('%d %b %Y')} | Time: {match.match_time}", styles['Normal']))
    if result:
        elements.append(Paragraph(f"<b>Final Score:</b> {result.our_score} - {result.opponent_score}", styles['Heading3']))
    elements.append(Spacer(1, 12))

    # --- STARTERS Table ---
    def build_lineup_table(title, lineup_qs):
        starters = lineup_qs.filter(is_starting=True)
        subs = lineup_qs.filter(is_starting=False)
        starter_data = [[f"{title} STARTING XI"]]
        for player in starters:
            starter_data.append([player.player.name])
        starter_table = Table(starter_data, colWidths=[250])
        starter_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ]))

        sub_data = [[f"{title} SUBSTITUTES"]]
        for player in subs:
            sub_data.append([player.player.name])
        sub_table = Table(sub_data, colWidths=[250])
        sub_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgreen),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ]))
        return starter_table, sub_table

    our_team_lineup = player_match_stats.filter(player__age_group=match.team)
    opponent_lineup = player_match_stats.exclude(player__age_group=match.team)

    our_starters_table, our_subs_table = build_lineup_table("Our Team", our_team_lineup)
    opp_starters_table, opp_subs_table = build_lineup_table("Opponent", opponent_lineup)

    elements.extend([Paragraph("<b>Lineups</b>", styles['Heading2'])])
    elements.append(Spacer(1, 6))
    elements.extend([our_starters_table, our_subs_table, Spacer(1, 12)])
    elements.extend([opp_starters_table, opp_subs_table, Spacer(1, 24)])

    # --- Goals Timeline Table ---
    elements.append(Paragraph("<b>Goals Timeline</b>", styles['Heading2']))
    goals_data = [['Minute', 'Scorer', 'Assist', 'Own Goal']]
    for goal in goals:
        goals_data.append([
            f"{goal.minute}'",
            goal.scorer.name if goal.scorer else '',
            goal.assist_by.name if goal.assist_by else '',
            'Yes' if goal.is_own_goal else 'No'
        ])
    if not goals:
        goals_data.append(['-', 'No goals', '-', '-'])

    goals_table = Table(goals_data, hAlign='LEFT', colWidths=[50, 150, 150, 50])
    goals_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.orange),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    elements.append(goals_table)
    elements.append(Spacer(1, 24))

    # --- Player Stats Table ---
    elements.append(Paragraph("<b>Player Statistics</b>", styles['Heading2']))
    stats_data = [['Player', 'Minutes', 'Goals', 'Assists', 'Yellows', 'Reds']]
    for stat in stats:
        goals_count = goals.filter(scorer=stat.player, is_own_goal=False).count()
        assists_count = goals.filter(assist_by=stat.player).count()
        stats_data.append([
            stat.player.name,
            stat.minutes_played,
            goals_count,
            assists_count,
            stat.yellow_cards,
            stat.red_cards
        ])

    stats_table = Table(stats_data, hAlign='LEFT')
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
    ]))
    elements.append(stats_table)

    # --- Optional: Draw watermark/logo using canvas hook ---
    def draw_background(canvas_obj, doc_obj):
        # Draw background image (transparent logo)
        bg_logo_path = os.path.join(settings.MEDIA_ROOT, 'team_logo', 'azam-cropped-transparent.png')
        if os.path.exists(bg_logo_path):
            canvas_obj.drawImage(ImageReader(bg_logo_path), 100, 250, width=400, height=400, preserveAspectRatio=True, mask='auto')

    # Frame & Page Template with background
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='normal')
    template = PageTemplate(id='with-logo', frames=[frame], onPage=draw_background)
    doc.addPageTemplates([template])

    doc.build(elements)
    return response




@login_required
def monthly_report_pdf(request, team):
    today = date.today()
    first_day = today.replace(day=1)
    last_day = today.replace(day=calendar.monthrange(today.year, today.month)[1])

    matches = Match.objects.filter(
        team=team,
        date__range=(first_day, last_day)
    ).order_by('date')

    stats = PlayerMatchStats.objects.filter(match__in=matches).select_related('player')
    goals = Goal.objects.filter(match__in=matches)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="monthly-report-{today.month}-{today.year}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    
    # --- Title ---
    title = Paragraph(f"<b>{team.upper()} - Monthly Match Report</b>", styles['Title'])
    date_range = Paragraph(f"<i>Period: {first_day.strftime('%d %b %Y')} to {last_day.strftime('%d %b %Y')}</i>", styles['Normal'])
    elements.extend([title, Spacer(1, 12), date_range, Spacer(1, 24)])

    # --- MATCH RESULTS TABLE ---
    elements.append(Paragraph("<b>Match Results</b>", styles['Heading2']))
    
    match_data = [['Date', 'Opponent', 'Venue', 'Result']]
    for match in matches:
        result = TeamMatchResult.objects.filter(match=match).first()
        scoreline = f"{result.our_score}-{result.opponent_score}" if result else "N/A"
        match_data.append([match.date.strftime('%d-%b-%Y'), match.opponent, match.venue, scoreline])

    match_table = Table(match_data, hAlign='LEFT')
    match_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    elements.extend([match_table, Spacer(1, 24)])

    # --- PLAYER STATISTICS TABLE ---
    elements.append(Paragraph("<b>Player Statistics</b>", styles['Heading2']))
    
    player_ids = stats.values_list('player', flat=True).distinct()
    player_data = [['Player', 'Apps', 'Minutes', 'Goals', 'Assists', 'Yellows', 'Reds']]

    for player in Player.objects.filter(id__in=player_ids):
        player_stats = stats.filter(player=player)
        total_minutes = player_stats.aggregate(Sum('minutes_played'))['minutes_played__sum'] or 0
        goals_count = goals.filter(scorer=player, is_own_goal=False).count()
        assists_count = goals.filter(assist_by=player).count()
        detailed_stats = PlayerDetailedAction.objects.filter(match__in=matches, player=player)
        yellow_cards = detailed_stats.aggregate(Sum('yellow_cards'))['yellow_cards__sum'] or 0
        red_cards = detailed_stats.aggregate(Sum('red_cards'))['red_cards__sum'] or 0

        player_data.append([
            player.name,
            player_stats.count(),
            total_minutes,
            goals_count,
            assists_count,
            yellow_cards,
            red_cards
        ])

    player_table = Table(player_data, hAlign='LEFT')
    player_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgreen),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
    ]))

    elements.append(player_table)

    doc.build(elements)
    return response

