from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from matches_app.models import Match
from matches_app.utils.match_details_utils import get_match_detail_context
from tagging_app.utils.pass_network_utils import get_pass_network_context


@login_required
def match_detail(request, match_id):
    match = get_object_or_404(Match, pk=match_id)

    # Prepare base context
    context = {
        'match': match,
    }

    # Get all the match-related context using the utility functions
    details_context = get_match_detail_context(match)
    pass_network_context = get_pass_network_context(match)

    # Merge all into one context dictionary
    context.update(details_context)
    context.update(pass_network_context)

    return render(request, 'matches_app/match_details.html', context)

