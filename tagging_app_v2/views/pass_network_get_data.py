from django.shortcuts import render, get_object_or_404
from matches_app.models import Match
from tagging_app_v2.models import PassEvent_v2
from django.db.models import Count, Q, F

def get_pass_data_view(request, match_id):
    match = get_object_or_404(Match, id=match_id)

    events = PassEvent_v2.objects.filter(match=match).select_related(
        "actor", "target", "receiver",
        "actor__team", "receiver__team", "target__team"
    )

    passes = events.filter(
    Q(action_type__in=["LOW_BALL", "HIGH_BALL"]) |
    Q(receiver__isnull=False, actor__team=F("receiver__team"))
)


    teams = [match.home_team, match.away_team]

    # Split stats by team
    team_stats = {}
    for team in teams:


        team_events = events.filter(actor__team=team)




        # -------------------------
        # TOTAL PASSES (same team)
        # -------------------------
        passes_qs = (
            team_events.filter(
                receiver__isnull=False,
                actor__team=F("receiver__team")
            )
            .values("actor__player__name")
            .annotate(total_passes=Count("id"))
        )

        # -------------------------
        # BALL LOST (actor loses)
        # -------------------------
        ball_lost_qs = (
            team_events.filter(
                Q(receiver__isnull=True) |
                ~Q(actor__team=F("receiver__team"))
            )
            .values("actor__player__name")
            .annotate(total_lost=Count("id"))
        )

        # -------------------------
        # BALL RECOVERY (receiver gains from opponent)
        # -------------------------
        ball_recovery_qs = (
            events.filter(
                Q(receiver__isnull=False) &
                ~Q(actor__team=F("receiver__team")) &
                Q(receiver__team=team)
            )
            .values("receiver__player__name")
            .annotate(total_recovery=Count("id"))
        )


        # -------------------------
        # MERGE ALL STATS
        # -------------------------
        player_stats = {}

        # Passes
        for p in passes_qs:
            player_stats[p["actor__player__name"]] = {
                "total_passes": p["total_passes"],
                "ball_lost": 0,
                "ball_recovery": 0
            }

        # Ball lost
        for p in ball_lost_qs:
            name = p["actor__player__name"]
            if name not in player_stats:
                player_stats[name] = {
                    "total_passes": 0,
                    "ball_lost": p["total_lost"],
                    "ball_recovery": 0
                }
            else:
                player_stats[name]["ball_lost"] = p["total_lost"]

        # Ball recovery
        for p in ball_recovery_qs:
            name = p["receiver__player__name"]
            if name not in player_stats:
                player_stats[name] = {
                    "total_passes": 0,
                    "ball_lost": 0,
                    "ball_recovery": p["total_recovery"]
                }
            else:
                player_stats[name]["ball_recovery"] = p["total_recovery"]






        # Pass matrix
        pass_matrix_qs = team_events.filter(
            receiver__isnull=False,
            actor__team=F("receiver__team")
        ).values( "actor__player__name", "receiver__player__name" ).annotate(total=Count("id"))

        # Convert to nested dict {actor: {receiver: count}}
        players = set()
        for e in pass_matrix_qs:
            players.update([e["actor__player__name"], e["receiver__player__name"]])
        players = sorted(players)

        matrix = {}
        for actor in players:
            matrix[actor] = {}
            for receiver in players:
                count = pass_matrix_qs.filter(actor__player__name=actor, receiver__player__name=receiver).aggregate(total=Count("id"))["total"] or 0
                matrix[actor][receiver] = count

        team_stats[team.name] = {
            "player_stats": player_stats,
            "pass_matrix": {
                "players": players,
                "matrix": matrix
            }
        }



    # Ball recovery (overall)
    ball_recovery = (
        events.filter(action_type="CLEARANCE")
        .values("actor__player__name")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    # Top five pass combinations (overall)
    top_five = sorted(
        passes.filter(receiver__isnull=False).values(
            "actor__player__name", "receiver__player__name"
        ).annotate(total=Count("id")), key=lambda x: x["total"], reverse=True
    )[:5]


    

    # =========================
    # =========================
    # AERIAL DUELS (HIGH_BALL)
    # =========================
    aerial_events = events.filter(action_type="HIGH_BALL")

    aerial_team_stats = {}

    for team in teams:

        team_aerial_stats = {}

        for ev in aerial_events:

            actor_team = ev.actor.team if ev.actor else None
            receiver_team = ev.receiver.team if ev.receiver else None
            target_team = ev.target.team if ev.target else None

            # ----------------------------
            # CASE 1: Same team → Receiver WON
            # ----------------------------
            if receiver_team and actor_team == receiver_team and receiver_team == team:

                name = ev.receiver.player.name
                team_aerial_stats.setdefault(name, {"won": 0, "lost": 0})
                team_aerial_stats[name]["won"] += 1

            # ----------------------------
            # CASE 2: Opponent duel
            # ----------------------------
            elif receiver_team and actor_team != receiver_team:

                # Receiver WON (only if belongs to this team)
                if receiver_team == team:
                    r_name = ev.receiver.player.name
                    team_aerial_stats.setdefault(r_name, {"won": 0, "lost": 0})
                    team_aerial_stats[r_name]["won"] += 1

                # Target LOST (only if belongs to this team)
                if ev.target and target_team == team and target_team == actor_team:
                    t_name = ev.target.player.name
                    team_aerial_stats.setdefault(t_name, {"won": 0, "lost": 0})
                    team_aerial_stats[t_name]["lost"] += 1

        aerial_team_stats[team.name] = team_aerial_stats


    #physical = duel_stats("BALL_SHIELDING")
    #one_vs_one = duel_stats("DRIBBLE")

    # Fouls
    fouls = events.filter(action_type="FOULS")
    fouls_committed = fouls.count()
    fouls_won = fouls.filter( Q(receiver__isnull=False) & ~Q(actor__team=F("receiver__team"))).count()


    context = {
        "match": match,
        "team_stats": team_stats,
        "ball_recovery": ball_recovery,
        "top_five": top_five,
        "aerial_team_stats": aerial_team_stats,
        #"physical": physical,
        #"one_vs_one": one_vs_one,
        "fouls_won": fouls_won,
        "fouls_committed": fouls_committed,
    }

    return render(request, "tagging_app_v2/pass_network_display_data.html", context)
