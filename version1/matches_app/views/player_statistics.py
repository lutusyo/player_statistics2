from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from version1.matches_app.models import Match, CompetitionType
from version1.teams_app.models import AgeGroup, Team
from version1.players_app.models import Player
from version1.lineup_app.models import MatchLineup
from version1.tagging_app.models import AttemptToGoal


@login_required
def player_statistics_view(request, team):

    # ======================
    # FILTERS FROM REQUEST
    # ======================
    selected_competition = request.GET.get('competition')
    selected_season = request.GET.get('season')
    selected_age_group = request.GET.get('age_group')

    # ======================
    # STATIC DATA FOR UI
    # ======================
    seasons = dict(Match._meta.get_field('season').choices)
    competitions = CompetitionType.choices
    age_groups = AgeGroup.objects.all()

    # ======================
    # OUR TEAM FILTERING
    # ======================
    age_group = AgeGroup.objects.get(code=team)

    our_teams = Team.objects.filter(
        age_group=age_group,
        team_type="OUR_TEAM"
    )

    # ONLY OUR PLAYERS
    players = Player.objects.filter(
        team__in=our_teams
    ).distinct()

    if selected_age_group:
        players = players.filter(age_group__code=selected_age_group)

    # ======================
    # BASE MATCH QUERY (IMPORTANT OPTIMIZATION)
    # ======================
    base_matches = Match.objects.filter(
        Q(home_team__in=our_teams) |
        Q(away_team__in=our_teams)
    )

    if selected_season:
        base_matches = base_matches.filter(season=selected_season)


    if selected_competition:
        base_matches = base_matches.filter(competition__type=selected_competition)

    if selected_age_group:
        base_matches = base_matches.filter(age_group__code=selected_age_group)

    # ======================
    # STATS FUNCTION
    # ======================
    def get_stats(player, competition_type):
        matches = base_matches.filter(
            competition__type=competition_type
        )
        

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

    # ======================
    # BUILD PLAYER DATA
    # ======================
    player_data = []

    for player in players:
        local = get_stats(player, CompetitionType.LOCAL_FRIENDLY)
        international = get_stats(player, CompetitionType.INTERNATIONAL_FRIENDLY)
        nbc = get_stats(player, CompetitionType.NBC_YOUTH_LEAGUE)

        total_ap = (
            local['appearances']
            + international['appearances']
            + nbc['appearances']
        )

        total_gl = (
            local['goals']
            + international['goals']
            + nbc['goals']
        )

        player_data.append({
            'player': player,

            'local_ap': local['appearances'],
            'local_gl': local['goals'],

            'int_ap': international['appearances'],
            'int_gl': international['goals'],

            'nbc_ap': nbc['appearances'],
            'nbc_gl': nbc['goals'],

            'total_ap': total_ap,
            'total_gl': total_gl,
        })

    # ======================
    # CONTEXT
    # ======================
    context = {
        'seasons': seasons,
        'competitions': competitions,
        'age_groups': age_groups,

        'selected_season': selected_season,
        'selected_age_group': selected_age_group,
        'selected_competition': selected_competition,

        'player_data': player_data,
        'team_selected': team,

        "active_tab": "statistics",
    }

    return render(request, 'matches_app/players_statistics.html', context)