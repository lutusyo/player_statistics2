from django.shortcuts import render, get_object_or_404
from matches_app.models import Match
from tagging_app.models import AttemptToGoal

# Mapping slugs to proper titles
REPORT_TITLES = {
    'post-match-summary': 'POST MATCH SUMMARY REPORT',
    'in-possession': 'IN POSSESSION',
    'out-of-possession': 'OUT OF POSSESSION',
    'goalkeeping': 'GOALKEEPING',
    'set-plays': 'SET PLAYS',
    'individual-in-possession': 'INDIVIDUAL DATA IN POSSESSION',
    'individual-out-of-possession': 'INDIVIDUAL DATA OUT OF POSSESSION',
    'individual-physical': 'INDIVIDUAL DATA PHYSICAL',
}

def get_match_goals(match):
    """
    Calculate goals for home and away using AttemptToGoal model.
    Only counts goals with outcome 'On Target Goal'.
    """
    home_goals = AttemptToGoal.objects.filter(
        match=match,
        team=match.home_team,
        outcome='On Target Goal'
    ).count()
    
    away_goals = AttemptToGoal.objects.filter(
        match=match,
        team=match.away_team,
        outcome='On Target Goal'
    ).count()
    
    return home_goals, away_goals

def get_match_result(match):
    home_goals, away_goals = get_match_goals(match)
    return home_goals, away_goals, f"{home_goals} - {away_goals}"

def intro_page_view(request, match_id, report_type):
    match = get_object_or_404(Match, id=match_id)

    # Handle unknown report_type
    if report_type not in REPORT_TITLES:
        return render(request, '404.html', status=404)

    # Calculate goals and result
    home_score, away_score, result = get_match_result(match)

    # Base context
    context = {
        'match': match,
        'home_team': match.home_team,
        'away_team': match.away_team,
        'title': REPORT_TITLES[report_type],
        'company': 'Azam Fc Analyst',
        'report_type': report_type,
        'home_score': home_score,
        'away_score': away_score,
        'result': result,
    }

    # Additional context for post-match summary
    if report_type == 'post-match-summary':
        context.update({
            'competition': match.competition_type,
            'venue': match.venue,
            'date': match.date,
            'kickoff_time': match.time,
            'season': match.season,
        })

    return render(request, 'reports_app/intro_page.html', context)
