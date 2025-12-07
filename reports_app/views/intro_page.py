from django.shortcuts import render, get_object_or_404
from gps_app.utils.gps_match_detail import get_gps_context
from reports_app.utils.stats import get_match_stats
from matches_app.models import Match
from tagging_app.utils.attempt_to_goal_utils_opp import get_opponent_goals_for_match
from tagging_app.utils.attempt_to_goal_utils import get_match_full_context

def get_dynamic_match_result(match, our_team_id):
    """
    Returns home_score, away_score, result string, and full context
    based on get_match_full_context.
    """
    full_context = get_match_full_context(match.id, our_team_id)
    our_team = full_context["our_team"]["obj"]
    opponent_team = full_context["opponent_team"]["obj"]

    our_goals = full_context["our_team"]["aggregate"]["attempts"]["total_goals"]
    opponent_goals = full_context["opponent_team"]["aggregate"]["attempts"]["total_goals"]

    # Align scores with home/away
    if match.home_team.id == our_team_id:
        home_score, away_score = our_goals, opponent_goals
    else:
        home_score, away_score = opponent_goals, our_goals

    return home_score, away_score, f"{home_score} - {away_score}", full_context


def in_possession_view(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    context = {
        'match': match,
        'title': REPORT_TITLES['in-possession'],
        'home_team': match.home_team,
        'away_team': match.away_team,
        'company': 'Azam Fc Analyst',
    }
    return render(request, 'reports_app/intro_pages/in_possession.html', context)


def out_of_possession_view(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    context = {
        'match': match,
        'title': REPORT_TITLES['out-of-possession'],
        'home_team': match.home_team,
        'away_team': match.away_team,
        'company': 'Azam Fc Analyst',
    }
    return render(request, 'reports_app/intro_pages/out_of_possession.html', context)


def goalkeeping_intro_view(request, match_id, return_context=False):
    match = get_object_or_404(Match, id=match_id)
    context = {
        'match': match,
        'title': REPORT_TITLES['goalkeeping'],
        'home_team': match.home_team,
        'away_team': match.away_team,
        'company': 'Azam Fc Analyst',
    }

    if return_context:
        return context
    return render(request, 'reports_app/match_report_templates/6_goalkeeping/goalkeeping_intro.html', context)


def set_plays_view(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    context = {
        'match': match,
        'title': REPORT_TITLES['set-plays'],
        'home_team': match.home_team,
        'away_team': match.away_team,
        'company': 'Azam Fc Analyst',
    }
    return render(request, 'reports_app/intro_pages/set_plays.html', context)


def individual_in_possession_view(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    context = {
        'match': match,
        'title': REPORT_TITLES['individual-in-possession'],
        'home_team': match.home_team,
        'away_team': match.away_team,
        'company': 'Azam Fc Analyst',
    }
    return render(request, 'reports_app/intro_pages/individual_in_possession.html', context)


def individual_out_of_possession_view(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    context = {
        'match': match,
        'title': REPORT_TITLES['individual-out-of-possession'],
        'home_team': match.home_team,
        'away_team': match.away_team,
        'company': 'Azam Fc Analyst',
    }
    return render(request, 'reports_app/intro_pages/individual_out_of_possession.html', context)


def individual_physical_view(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    gps_context = get_gps_context(match)
    stats_context = get_match_stats(match)

    context = {
        'match': match,
        'title': REPORT_TITLES['individual-physical'],
        'home_team': match.home_team,
        'away_team': match.away_team,
        'company': 'Azam Fc Analyst',
        **gps_context,
        **stats_context,
    }
    return render(request, 'reports_app/intro_pages/individual_physical.html', context)


def intro_page_view(request, match_id, report_type, our_team_id=None):
    match = get_object_or_404(Match, id=match_id)

    if report_type not in REPORT_TITLES:
        return render(request, '404.html', status=404)

    # Default to home team if our_team_id not provided
    if not our_team_id:
        our_team_id = match.home_team.id

    home_score, away_score, result, _ = get_dynamic_match_result(match, our_team_id)

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

    if report_type == 'post-match-summary':
        context.update({
            'competition': match.competition_type,
            'venue': match.venue,
            'date': match.date,
            'kickoff_time': match.time,
            'season': match.season,
        })

    if report_type == 'individual-physical':
        gps_context = get_gps_context(match)
        context.update(gps_context)

    return render(request, 'reports_app/intro_page.html', context)
