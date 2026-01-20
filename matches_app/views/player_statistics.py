from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from matches_app.models import Match, CompetitionType
from teams_app.models import AgeGroup
from players_app.models import Player
from lineup_app.models import MatchLineup
from tagging_app.models import AttemptToGoal


@login_required
def player_statistics_view(request, team):
    selected_season = request.GET.get('season')
    selected_age_group = request.GET.get('age_group')

    seasons = dict(Match._meta.get_field('season').choices)
    competitions = CompetitionType.choices
    age_groups = AgeGroup.objects.all()

    players = Player.objects.filter(age_group__code=team)

    if selected_age_group:
        players = players.filter(age_group__code=selected_age_group)

    def get_stats(player, competition_type):
        matches = Match.objects.filter(
            competition__type=competition_type
        )

        if selected_season:
            matches = matches.filter(season=selected_season)

        if selected_age_group:
            matches = matches.filter(age_group__code=selected_age_group)

        appearances = MatchLineup.objects.filter(
            player=player,
            match__in=matches
        ).count()

        goals = AttemptToGoal.objects.filter(
            player=player,
            match__in=matches,
            outcome='On Target Goal'
        ).count()

        return {
            'appearances': appearances,
            'goals': goals
        }

    player_data = []

    for player in players:
        local = get_stats(player, CompetitionType.LOCAL_FRIENDLY)
        international = get_stats(player, CompetitionType.INTERNATIONAL_FRIENDLY)
        nbc = get_stats(player, CompetitionType.NBC_YOUTH_LEAGUE)

        player_data.append({
            'player': player,

            'local_ap': local['appearances'],
            'local_gl': local['goals'],

            'int_ap': international['appearances'],
            'int_gl': international['goals'],

            'nbc_ap': nbc['appearances'],
            'nbc_gl': nbc['goals'],

            'total_ap': (
                local['appearances']
                + international['appearances']
                + nbc['appearances']
            ),
            'total_gl': (
                local['goals']
                + international['goals']
                + nbc['goals']
            ),
        })

    context = {
        'seasons': seasons,
        'competitions': competitions,
        'age_groups': age_groups,
        'selected_season': selected_season,
        'selected_age_group': selected_age_group,
        'player_data': player_data,
        'team_selected': team,
    }

    return render(request, 'matches_app/players_statistics.html', context)
