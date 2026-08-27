from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from version1.reports_app.forms import PlayerPerformancePotentialRatingForm
from version1.reports_app.models.rating import PlayerPerformancePotentialRating

from version1.teams_app.models import Team
from version1.players_app.models import Player

@login_required
def rate_player(request, team_id, player_id):

    team = get_object_or_404(
        Team,
        id=team_id
    )

    season = request.GET.get('season')

    if not season:
        return redirect(
            'reports_app:player_rating_list',
            team_id=team.id,
        )

    player = get_object_or_404(
        Player,
        id=player_id,
        team=team,
        is_active=True,
    )

    if request.method == 'POST':

        form = PlayerPerformancePotentialRatingForm(
            request.POST
        )

        if form.is_valid():

            rating = form.save(commit=False)

            rating.player = player
            rating.team = team
            rating.season = season

            # We will connect this to StaffMember later.
            rating.rated_by = None

            rating.save()

            messages.success(
                request,
                f"{player.full_name} rating saved successfully."
            )

            return redirect(
                f"{reverse('reports_app:player_rating_list', kwargs={'team_id': team.id})}"
                f"?season={season}"
            )

    else:
        form = PlayerPerformancePotentialRatingForm()

    context = {
        'player': player,
        'team': team,
        'season': season,
        'form': form,
    }

    return render(
        request,
        'reports_app/team_reports/rate_player.html',
        context
    )

@login_required
def player_rating_list(request, team_id):

    team = get_object_or_404(
        Team,
        id=team_id
    )

    season = request.GET.get('season')

    if not season:
        return render(
            request,
            'reports_app/team_reports/player_rating_list.html',
            {
                'team': team,
                'season': None,
                'players': [],
                'error': 'Please select a season.',
            }
        )

    # ---------------------------------------------------------
    # SAVE RATING FROM THE LISTING PAGE
    # ---------------------------------------------------------

    if request.method == 'POST':

        player_id = request.POST.get('player_id')
        performance = request.POST.get('performance')
        potential = request.POST.get('potential')
        notes = request.POST.get('notes', '').strip()

        player = get_object_or_404(
            Player,
            id=player_id,
            team=team,
            is_active=True,
        )

        # Basic validation
        if performance not in ['1', '2', '3']:
            messages.error(
                request,
                f"Invalid performance rating for {player.full_name}."
            )

            return redirect(
                f"{reverse('reports_app:player_rating_list', kwargs={'team_id': team.id})}"
                f"?season={season}"
            )

        if potential not in ['1', '2', '3']:
            messages.error(
                request,
                f"Invalid potential rating for {player.full_name}."
            )

            return redirect(
                f"{reverse('reports_app:player_rating_list', kwargs={'team_id': team.id})}"
                f"?season={season}"
            )

        # -----------------------------------------------------
        # CREATE A NEW RATING
        # -----------------------------------------------------

        PlayerPerformancePotentialRating.objects.create(
            player=player,
            team=team,
            season=season,
            performance=int(performance),
            potential=int(potential),
            notes=notes,
            rated_by=None,
        )

        messages.success(
            request,
            f"{player.full_name} rating saved successfully."
        )

        return redirect(
            f"{reverse('reports_app:player_rating_list', kwargs={'team_id': team.id})}"
            f"?season={season}"
        )

    # ---------------------------------------------------------
    # GET PLAYERS
    # ---------------------------------------------------------

    players_queryset = (
        Player.objects
        .filter(
            team=team,
            is_active=True,
        )
        .order_by(
            'name',
            'second_name',
            'surname',
        )
    )

    players = []

    for player in players_queryset:

        latest_rating = (
            PlayerPerformancePotentialRating.objects
            .filter(
                player=player,
                team=team,
                season=season,
            )
            .order_by('-rated_at')
            .first()
        )

        players.append({
            'player': player,
            'rating': latest_rating,
        })

    return render(
        request,
        'reports_app/team_reports/player_rating_list.html',
        {
            'team': team,
            'season': season,
            'players': players,
        }
    )