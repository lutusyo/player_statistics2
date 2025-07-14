from django.conf import settings
from django.shortcuts import render, get_object_or_404
from .models import Match, Goal, PlayerMatchStats, TeamMatchResult
from players_app.models import PlayerCareerStage, Player
from django.db.models import Sum, Count
from django.contrib.auth.decorators import login_required
from datetime import date
from gps_app.models import GPSRecord
import csv
from django.http import HttpResponse
from .models import Match, PlayerMatchStats
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
import os


@login_required
def team_dashboard(request, team):
    players = Player.objects.filter(age_group=team)

    position_order = ['Goalkeeper', 'Defender', 'Midfielder', 'Forward']
    selected_age_group = request.GET.get('age_group')


    #group players by position

    grouped_players = {}
    for position in position_order:
        grouped_players[position] = players.filter(position=position)



    context = {
        'team_selected': team,
        'selected_age_group': selected_age_group,
        'players': players,
        'position_order': position_order,
        'grouped_players': grouped_players,
        'active_tab': 'fixtures'
    }
    return render(request, 'matches_app/fixtures.html', context)


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

                #distribution
                'total_passes': player_stats.aggregate(Sum('total_passes'))['total_passes__sum'] or 0,
                'pass_success_rate': round(player_stats.aggregate(Sum('pass_success_rate'))['pass_success_rate__sum'] or 0, 2),
                'long_pass_success': round(player_stats.aggregate(Sum('long_pass_success'))['long_pass_success__sum'] or 0, 2),

                # discpline
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
    goals = Goal.objects.filter(match=match).select_related('scorer', 'assist_by')
    team_result = TeamMatchResult.objects.filter(match=match).first()
    player_stats = PlayerMatchStats.objects.filter(match=match).select_related('player')

    return render(request, 'matches_app/match_details.html', {
        'match': match,
        'goals': goals,
        'team_result': team_result,
        'player_stats': player_stats,
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

def export_match_summary_pdf(request, match_id):
    match = get_object_or_404(Match, pk=match_id)
    goals = Goal.objects.filter(match=match).select_related('scorer', 'assist_by')
    stats = PlayerMatchStats.objects.filter(match=match).select_related('player')
    result = TeamMatchResult.objects.filter(match=match).first()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="match-summary-{match.id}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    y = height - 50

    # Team logos
    if match.our_team_logo:
        our_logo_path = os.path.join(settings.MEDIA_ROOT, match.our_team_logo.name)
        if os.path.exists(our_logo_path):
            p.drawImage(ImageReader(our_logo_path), 50, y - 60, width=80, height=80, preserveAspectRatio=True)

    if match.opponent_logo:
        opponent_logo_path = os.path.join(settings.MEDIA_ROOT, match.opponent_logo.name)
        if os.path.exists(opponent_logo_path):
            p.drawImage(ImageReader(opponent_logo_path), width - 130, y - 60, width=80, height=80, preserveAspectRatio=True)

    # Match title
    p.setFont("Helvetica-Bold", 14)
    p.drawCentredString(width / 2, y, f"{match.get_team_display()} vs {match.opponent}")
    y -= 100

    # Match details
    p.setFont("Helvetica", 12)
    if result:
        p.drawString(50, y, f"Score: {result.our_score} - {result.opponent_score}")
        y -= 20
    p.drawString(50, y, f"Venue: {match.venue}")
    y -= 20
    p.drawString(50, y, f"Date: {match.date} | Time: {match.match_time}")
    y -= 30

    # Line-ups
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Line-up")
    y -= 20
    p.setFont("Helvetica", 10)

    our_team_players = stats.filter(player__age_group=match.team)
    opponent_players = stats.exclude(player__age_group=match.team)


    def split_lineup(queryset):
        starters = queryset.filter(is_starting=True) if hasattr(PlayerMatchStats, 'is_starting') else queryset[:11]
        subs = queryset.exclude(pk__in=starters.values_list('pk', flat=True))
        return starters, subs

    our_starters, our_subs = split_lineup(our_team_players)
    opp_starters, opp_subs = split_lineup(opponent_players)

    p.drawString(60, y, "Our Team")
    p.drawString(width / 2 + 20, y, "Opponent Team")
    y -= 15

    max_lines = max(len(our_starters) + len(our_subs), len(opp_starters) + len(opp_subs))
    for i in range(max_lines):
        if y < 100:
            p.showPage()
            y = height - 50
            p.setFont("Helvetica", 10)

        left = ""
        right = ""

        if i < len(our_starters):
            left = f"⚽ {our_starters[i].player.name}"
        elif i - len(our_starters) < len(our_subs):
            left = f"↩ {our_subs[i - len(our_starters)].player.name}"

        if i < len(opp_starters):
            right = f"⚽ {opp_starters[i].player.name}"
        elif i - len(opp_starters) < len(opp_subs):
            right = f"↩ {opp_subs[i - len(opp_starters)].player.name}"

        p.drawString(60, y, left)
        p.drawString(width / 2 + 20, y, right)
        y -= 15

    y -= 20
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Goals Timeline:")
    y -= 20
    p.setFont("Helvetica", 10)
    if goals:
        for goal in goals:
            if y < 100:
                p.showPage()
                y = height - 50
            text = f"{goal.minute}': "
            if goal.is_own_goal:
                text += f"Own Goal by {goal.scorer}"
            else:
                text += f"{goal.scorer}"
                if goal.assist_by:
                    text += f" (Assist: {goal.assist_by})"
            p.drawString(60, y, text)
            y -= 15
    else:
        p.drawString(60, y, "No goals recorded.")
        y -= 20

    y -= 20
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Player Statistics:")
    y -= 20
    p.setFont("Helvetica", 10)
    for stat in stats:
        if y < 100:
            p.showPage()
            y = height - 50
        p.drawString(60, y, f"{stat.player.name} - Minutes: {stat.minutes_played}, Goals: {stat.goals}, Assists: {stat.assists}, Yellows: {stat.yellow_cards}, Reds: {stat.red_cards}")
        y -= 15

    p.showPage()
    p.save()
    return response






