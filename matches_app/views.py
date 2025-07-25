from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
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
from actions_app.models import TeamActionStats, PlayerDetailedAction



from datetime import date, timedelta
from django.utils.timezone import now
from django.http import HttpResponse
from .models import Match, PlayerMatchStats, Goal
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from django.contrib.auth.decorators import login_required
import calendar


from PIL import Image

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

    original_logo_path = os.path.join(settings.MEDIA_ROOT, 'team_logo', 'azam-cropped-logo.png')
    transparent_logo_path = os.path.join(settings.MEDIA_ROOT, 'team_logo', 'azam-cropped-transparent.png')

    # Create transparent version if not already created
    if not os.path.exists(transparent_logo_path):
        create_transparent_image(original_logo_path, transparent_logo_path, opacity=0.005)

    background_logo_path = transparent_logo_path

    match = get_object_or_404(Match, pk=match_id)
    goals = Goal.objects.filter(match=match).select_related('scorer', 'assist_by')

    stats = PlayerDetailedAction.objects.filter(match=match).select_related('player')
    result = TeamMatchResult.objects.filter(match=match).first()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="match-summary-{match.id}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    y = height - 50
    draw_background(p, background_logo_path, width, height)

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
    y -= 20
    p.setFont("Helvetica", 10)

    # Get all PlayerMatchStats for this match
    player_match_stats = PlayerMatchStats.objects.filter(match=match).select_related('player')

    # Separate lineups by team
    our_team_lineup = player_match_stats.filter(player__age_group=match.team)
    opponent_lineup = player_match_stats.exclude(player__age_group=match.team)

    # Now split each group into starters and subs
    def split_lineup(lineup):
        starters = lineup.filter(is_starting=True)
        subs = lineup.filter(is_starting=False)
        return starters, subs

    our_starters, our_subs = split_lineup(our_team_lineup)
    opp_starters, opp_subs = split_lineup(opponent_lineup)

    # Draw Line-up Titles
    p.drawString(60, y, "STARTING")
    p.drawString(width / 2 + 20, y, "STARTING")
    y -= 15

    # Print Starters
    max_starters = max(len(our_starters), len(opp_starters))
    for i in range(max_starters):
        if y < 100:
            p.showPage()
            draw_background(p, background_logo_path, width, height)
            y = height - 50
            p.setFont("Helvetica", 10)

        left = our_starters[i].player.name if i < len(our_starters) else ""
        right = opp_starters[i].player.name if i < len(opp_starters) else ""
        p.drawString(60, y, f"⚽ {left}")
        p.drawString(width / 2 + 20, y, f"⚽ {right}")
        y -= 15

    # Substitutes Heading
    y -= 10
    p.setFont("Helvetica-Bold", 12)
    p.drawString(60, y, "SUBSTITUTES")
    p.drawString(width / 2 + 20, y, "SUBSTITUTES")
    y -= 15
    p.setFont("Helvetica", 10)

    # Print Substitutes
    max_subs = max(len(our_subs), len(opp_subs))
    for i in range(max_subs):
        if y < 100:
            p.showPage()
            draw_background(p, background_logo_path, width, height)
            y = height - 50
            p.setFont("Helvetica", 10)

        left = our_subs[i].player.name if i < len(our_subs) else ""
        right = opp_subs[i].player.name if i < len(opp_subs) else ""
        p.drawString(60, y, f"↩ {left}")
        p.drawString(width / 2 + 20, y, f"↩ {right}")
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
                draw_background(p, background_logo_path, width, height)
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

    # Updated loop for player stats with goal and assist counts fetched from Goal model
    for stat in stats:
        if y < 100:
            p.showPage()
            draw_background(p, background_logo_path, width, height)
            y = height - 50

        goals_count = Goal.objects.filter(match=match, scorer=stat.player, is_own_goal=False).count()
        assists_count = Goal.objects.filter(match=match, assist_by=stat.player).count()

        p.drawString(
            60, y,
            f"{stat.player.name} - Minutes: {stat.minutes_played}, Goals: {goals_count}, Assists: {assists_count}, "
            f"Yellows: {stat.yellow_cards}, Reds: {stat.red_cards}"
        )
        y -= 15

    p.showPage()
    p.save()
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

    stats = PlayerMatchStats.objects.filter(
        match__in=matches
    ).select_related('player')

    goals = Goal.objects.filter(match__in=matches)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="monthly-report-{today.month}-{today.year}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    y = height - 50

    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width / 2, y, f"{team.upper()} - Monthly Match Report")
    y -= 30
    p.setFont("Helvetica", 12)
    p.drawString(50, y, f"Period: {first_day.strftime('%d %b %Y')} to {last_day.strftime('%d %b %Y')}")
    y -= 40

    # --- MATCH SUMMARY ---
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, "Match Results")
    y -= 20
    p.setFont("Helvetica", 10)

    for match in matches:
        if y < 100:
            p.showPage()
            y = height - 50
        
    
        result = TeamMatchResult.objects.filter(match=match).first()


        scoreline = f"{result.our_score}-{result.opponent_score}" if result else "N/A"
        p.drawString(50, y, f"{match.date} | vs {match.opponent} | Venue: {match.venue} | Result: {scoreline}")
        y -= 15

    # --- PLAYER STATISTICS ---
    y -= 20
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, "Player Statistics")
    y -= 20
    p.setFont("Helvetica", 10)

    players = stats.values_list('player', flat=True).distinct()
    
    for player in Player.objects.filter(id__in=players):
        player_stats = stats.filter(player=player)
        total_minutes = player_stats.aggregate(Sum('minutes_played'))['minutes_played__sum'] or 0
        goals_count = goals.filter(scorer=player, is_own_goal=False).count()
        assists_count = goals.filter(assist_by=player).count()

        detailed_stats = PlayerDetailedAction.objects.filter(match__in=matches, player=player)

        yellow_cards = detailed_stats.aggregate(Sum('yellow_cards'))['yellow_cards__sum'] or 0
        red_cards = detailed_stats.aggregate(Sum('red_cards'))['red_cards__sum'] or 0

        if y < 100:
            p.showPage()
            y = height - 50

        p.drawString(60, y, f"{player.name} - Apps: {player_stats.count()}, Mins: {total_minutes}, Goals: {goals_count}, Assists: {assists_count}, Yellows: {yellow_cards}, Reds: {red_cards}")
        y -= 15

    p.save()
    return response

