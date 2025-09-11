from django.db.models import Count, Q
from defensive_app.models import PlayerDefensiveStats
from tagging_app.models import AttemptToGoal, PassEvent
from gps_app.models import GPSRecord   # assuming you have this for distance

def get_match_summary(match, our_team, opponent_team):
    """Return aggregated match summary stats for both teams."""

    summary = {
        "our_team": {"name": our_team.name},
        "opponent_team": {"name": opponent_team.name},
    }

    # 🔹 GOALS & ATTEMPTS
    for team_key, team in [("our_team", our_team), ("opponent_team", opponent_team)]:
        attempts = AttemptToGoal.objects.filter(match=match, team=team)

        summary[team_key]["goals"] = attempts.filter(outcome="On Target Goal").count()
        summary[team_key]["attempts_total"] = attempts.count()
        summary[team_key]["on_target"] = attempts.filter(outcome__in=["On Target Saved", "On Target Goal"]).count()
        summary[team_key]["off_target"] = attempts.filter(outcome="Off Target").count()
        summary[team_key]["blocked"] = attempts.filter(outcome="Blocked").count()

    # 🔹 PASSES
    for team_key, team in [("our_team", our_team), ("opponent_team", opponent_team)]:
        passes = PassEvent.objects.filter(match=match, from_team=team)
        summary[team_key]["total_passes"] = passes.count()
        summary[team_key]["successful_passes"] = passes.filter(is_successful=True).count()
        summary[team_key]["pass_accuracy"] = (
            round((summary[team_key]["successful_passes"] / passes.count()) * 100, 1)
            if passes.count() > 0 else 0
        )
        summary[team_key]["crosses"] = passes.filter(from_team=team, is_successful=True,).count()

    # 🔹 DEFENSIVE STATS
    for team_key, team in [("our_team", our_team), ("opponent_team", opponent_team)]:
        defensive = PlayerDefensiveStats.objects.filter(match=match, player__team=team)

        summary[team_key]["tackles_attempted"] = (
            defensive.aggregate(total=Count("tackle_won") + Count("tackle_lost"))["total"]
            if defensive.exists() else 0
        )
        summary[team_key]["tackles_won"] = defensive.aggregate(total=Count("tackle_won"))["total"] or 0

        summary[team_key]["fouls_committed"] = defensive.aggregate(total=Count("foul_committed"))["total"] or 0
        summary[team_key]["yellow_cards"] = defensive.aggregate(total=Count("yellow_card"))["total"] or 0
        summary[team_key]["red_cards"] = defensive.aggregate(total=Count("red_card"))["total"] or 0

    # 🔹 DISTANCE COVERED (if GPS app exists)
    try:
        for team_key, team in [("our_team", our_team), ("opponent_team", opponent_team)]:
            gps_qs = GPSRecord.objects.filter(match=match, player__team=team)
            summary[team_key]["total_distance"] = gps_qs.aggregate(total=Sum("distance"))["total"] or 0
    except:
        summary["gps_data"] = "Not available"

    return summary
