from django.shortcuts import render, get_object_or_404
from matches_app.models import Match
from lineup_app.models import MatchLineup, Substitution


def match_lineup_report(request, match_id, return_context=False):
    match = get_object_or_404(Match, id=match_id)

    # Helper to attach sub in/out minutes to lineup
    def annotate_subs(lineup_qs):
        lineup = []
        for ml in lineup_qs:
            sub_in_minute = None
            sub_out_minute = None

            # Check if player was substituted in
            sub_in = Substitution.objects.filter(match=match, player_in=ml).first()
            if sub_in:
                sub_in_minute = sub_in.minute

            # Check if player was substituted out
            sub_out = Substitution.objects.filter(match=match, player_out=ml).first()
            if sub_out:
                sub_out_minute = sub_out.minute

            lineup.append({
                "player": ml.player,
                "minutes_played": ml.minutes_played,
                "sub_in_minute": sub_in_minute,
                "sub_out_minute": sub_out_minute,
            })
        return lineup

    # HOME TEAM
    home_starting_qs = MatchLineup.objects.filter(match=match, team=match.home_team, is_starting=True).order_by("order")
    home_subs_qs = MatchLineup.objects.filter(match=match, team=match.home_team, is_starting=False).order_by("order")
    home_starting = annotate_subs(home_starting_qs)
    home_subs = annotate_subs(home_subs_qs)

    # AWAY TEAM
    away_starting_qs = MatchLineup.objects.filter(match=match, team=match.away_team, is_starting=True).order_by("order")
    away_subs_qs = MatchLineup.objects.filter(match=match, team=match.away_team, is_starting=False).order_by("order")
    away_starting = annotate_subs(away_starting_qs)
    away_subs = annotate_subs(away_subs_qs)

    context = {
        "match": match,
        "home_starting": home_starting,
        "home_subs": home_subs,
        "away_starting": away_starting,
        "away_subs": away_subs,
    }

    if return_context:
        return context

    return render(request, "reports_app/match_report_templates/2_match_summary_team/match_summary_team.html", context)

