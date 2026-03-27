from collections import defaultdict

from django.shortcuts import get_object_or_404
from django.http import Http404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from matches_app.models import Match
from players_app.models import Player
from defensive_app.models import PlayerDefensiveStats
from tagging_app.models import AttemptToGoal, PassEvent, GoalkeeperDistributionEvent
from lineup_app.models import MatchLineup, Substitution

from teams_app.models import Team




class PlayerDetailAPIView(APIView):
    """
    API view that returns full player details, statistics,
    match-by-match performance and measurements.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, player_id):
        # --------------------------------------------------
        # Player
        # --------------------------------------------------
        player = get_object_or_404(Player, id=player_id)

        if not player.is_active:
            raise Http404("This player is inactive")

        related_players = Player.objects.filter(
            age_group=player.age_group,
            is_active=True
        ).exclude(id=player.id)

        selected_season = request.GET.get('season', 'all')
        selected_competition = request.GET.get('competition', 'all')

        # --------------------------------------------------
        # Helper filter
        # --------------------------------------------------
        def apply_match_filters(qs):
            if selected_season != 'all':
                qs = qs.filter(match__season=selected_season)
            if selected_competition != 'all':
                qs = qs.filter(match__competition_type=selected_competition)
            return qs

        # --------------------------------------------------
        # QuerySets
        # --------------------------------------------------
        lineup_qs = apply_match_filters(
            MatchLineup.objects.filter(player=player).select_related('match')
        )

        goals_qs = apply_match_filters(
            AttemptToGoal.objects.filter(
                player=player,
                outcome='On Target Goal',
                is_own_goal=False
            ).select_related('match')
        )

        assists_qs = apply_match_filters(
            AttemptToGoal.objects.filter(
                assist_by=player,
                outcome='On Target Goal',
                is_own_goal=False
            ).select_related('match')
        )

        defensive_qs = apply_match_filters(
            PlayerDefensiveStats.objects.filter(player=player).select_related('match')
        )

        attempts_qs = apply_match_filters(
            AttemptToGoal.objects.filter(player=player).select_related('match')
        )

        passes_qs = apply_match_filters(
            PassEvent.objects.filter(from_player=player).select_related('match')
        )

        gk_dist_qs = apply_match_filters(
            GoalkeeperDistributionEvent.objects.filter(goalkeeper=player).select_related('match')
        )

        subs_in_qs = apply_match_filters(
            Substitution.objects.filter(player_in__player=player).select_related('match')
        )

        subs_out_qs = apply_match_filters(
            Substitution.objects.filter(player_out__player=player).select_related('match')
        )

        # --------------------------------------------------
        # Match IDs
        # --------------------------------------------------
        lineup_match_ids = set(lineup_qs.values_list('match_id', flat=True))
        goals_match_ids = set(goals_qs.values_list('match_id', flat=True))
        assists_match_ids = set(assists_qs.values_list('match_id', flat=True))
        defensive_match_ids = set(defensive_qs.values_list('match_id', flat=True))
        subs_in_match_ids = set(subs_in_qs.values_list('match_id', flat=True))
        subs_out_match_ids = set(subs_out_qs.values_list('match_id', flat=True))

        all_match_ids = (
            lineup_match_ids
            | goals_match_ids
            | assists_match_ids
            | defensive_match_ids
            | subs_in_match_ids
            | subs_out_match_ids
        )

        matches = Match.objects.filter(id__in=all_match_ids)

        # --------------------------------------------------
        # Stats dictionary
        # --------------------------------------------------
        stats_dict = defaultdict(lambda: {
            'appearances': 0,
            'minutes': 0,
            'starts': 0,
            'sub_in': 0,
            'sub_out': 0,
            'goals': 0,
            'assists': 0,
            'tackles_won': 0,
            'tackles_lost': 0,
            'yellow_cards': 0,
            'red_cards': 0
        })

        # --------------------------------------------------
        # Lineups grouped by match
        # --------------------------------------------------
        lineups_by_match = defaultdict(list)
        for lu in lineup_qs:
            lineups_by_match[lu.match_id].append(lu)

        subs_in_by_match = defaultdict(int)
        for s in subs_in_qs:
            subs_in_by_match[s.match_id] += 1

        subs_out_by_match = defaultdict(int)
        for s in subs_out_qs:
            subs_out_by_match[s.match_id] += 1

        # --------------------------------------------------
        # Appearances & minutes
        # --------------------------------------------------
        for match in matches:
            comp = match.competition_type or "Unknown"
            stats = stats_dict[comp]

            final_minute = 90
            if hasattr(match, "elapsed_minutes") and callable(match.elapsed_minutes):
                try:
                    final_minute = match.elapsed_minutes()
                except Exception:
                    pass

            mp_for_match = 0
            starts_for_match = 0

            if match.id in lineups_by_match:
                for lu in lineups_by_match[match.id]:
                    mp = lu.calculate_minutes_played(final_minute=final_minute)
                    if not mp and getattr(lu, "minutes_played", 0):
                        mp = lu.minutes_played
                    mp_for_match += mp or 0
                    if lu.is_starting:
                        starts_for_match += 1

            played = (
                mp_for_match > 0
                or match.id in goals_match_ids
                or match.id in assists_match_ids
                or match.id in defensive_match_ids
                or match.id in subs_in_by_match
                or match.id in subs_out_by_match
            )

            if played:
                stats['appearances'] += 1
                stats['minutes'] += mp_for_match
                stats['starts'] += starts_for_match
                stats['sub_in'] += subs_in_by_match.get(match.id, 0)
                stats['sub_out'] += subs_out_by_match.get(match.id, 0)

        # --------------------------------------------------
        # Goals & assists
        # --------------------------------------------------
        for g in goals_qs:
            comp = g.match.competition_type or "Unknown"
            stats_dict[comp]['goals'] += 1

        for a in assists_qs:
            comp = a.match.competition_type or "Unknown"
            stats_dict[comp]['assists'] += 1

        # --------------------------------------------------
        # Defensive stats
        # --------------------------------------------------
        for d in defensive_qs:
            comp = d.match.competition_type or "Unknown"
            s = stats_dict[comp]
            s['tackles_won'] += d.tackle_won or 0
            s['tackles_lost'] += d.tackle_lost or 0
            s['yellow_cards'] += d.yellow_card or 0
            s['red_cards'] += d.red_card or 0

        # --------------------------------------------------
        # Match-by-match performance
        # --------------------------------------------------
        goals_by_match = defaultdict(int)
        assists_by_match = defaultdict(int)
        shots_by_match = defaultdict(int)
        passes_by_match = defaultdict(int)

        for g in goals_qs:
            goals_by_match[g.match_id] += 1
        for a in assists_qs:
            assists_by_match[a.match_id] += 1
        for a in attempts_qs:
            shots_by_match[a.match_id] += 1
        for p in passes_qs:
            passes_by_match[p.match_id] += 1

        matches_played = []
        for match in matches:
            lineup = MatchLineup.objects.filter(match=match, player=player).first()

            if match.home_team and match.home_team.team_type == 'OPPONENT':
                opponent = match.home_team
            elif match.away_team and match.away_team.team_type == 'OPPONENT':
                opponent = match.away_team
            else:
                opponent = None

            matches_played.append({
                "match_id": match.id,
                "date": match.date,
                "competition": match.competition_type,
                "season": match.season,
                "opponent": opponent.name if opponent else "Unknown",
                "minutes_played": lineup.minutes_played if lineup else 0,
                "goals": goals_by_match.get(match.id, 0),
                "assists": assists_by_match.get(match.id, 0),
                "shots": shots_by_match.get(match.id, 0),
                "passes": passes_by_match.get(match.id, 0),
            })

        # --------------------------------------------------
        # Response
        # --------------------------------------------------
        return Response({
            "player": {
                "id": player.id,
                "full_name": player.full_name,
                "position": player.position,
                "age": player.age_using_birthdate,
                "photo": player.photo.url if player.photo else None,
                "bmi": player.bmi,
            },
            "filters": {
                "season": selected_season,
                "competition": selected_competition,
            },
            "stats_by_competition": stats_dict,
            "matches_played": matches_played,
            "measurements": {
                "latest": player.current_measurement,
                "last_three": player.last_three_measurements,
            },
            "related_players": [
                {
                    "id": p.id,
                    "name": p.full_name,
                    "position": p.position
                } for p in related_players
            ]
        })
