from django.shortcuts import render, get_object_or_404
from lineup_app.models import Match, MatchLineup, Substitution
from tagging_app.models import AttemptToGoal, PassEvent  # adjust to your app name

def match_summary_view(request, match_id):
    match = get_object_or_404(Match, id=match_id)

    # Goals
    goals = AttemptToGoal.objects.filter(match=match, outcome='On Target Goal')

    home_goals = goals.filter(team=match.home_team).count()
    away_goals = goals.filter(team=match.away_team).count()

    # Lineups
    home_starting = MatchLineup.objects.filter(match=match, team=match.home_team, is_starting=True)
    home_subs = MatchLineup.objects.filter(match=match, team=match.home_team, is_starting=False)
    away_starting = MatchLineup.objects.filter(match=match, team=match.away_team, is_starting=True)
    away_subs = MatchLineup.objects.filter(match=match, team=match.away_team, is_starting=False)

    # Substitutions
    home_substitutions = Substitution.objects.filter(match=match, team=match.home_team)
    away_substitutions = Substitution.objects.filter(match=match, team=match.away_team)

    # Pass Events (for chart)
    pass_events = PassEvent.objects.filter(match=match)

    context = {
        'match': match,
        'home_goals': home_goals,
        'away_goals': away_goals,
        'home_starting': home_starting,
        'home_subs': home_subs,
        'away_starting': away_starting,
        'away_subs': away_subs,
        'home_substitutions': home_substitutions,
        'away_substitutions': away_substitutions,
        'pass_events': pass_events,
    }
    return render(request, 'reports_app/match_summary.html', context)
