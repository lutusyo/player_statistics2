from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect, render

from version1.matches_app.forms import MatchResultForm
from version1.matches_app.models import Match


@staff_member_required
def match_result_update(request, match_id):

    match = get_object_or_404(
        Match.objects.select_related(
            "home_team",
            "away_team",
            "competition_season",
        ),
        id=match_id,
    )

    if request.method == "POST":

        form = MatchResultForm(
            request.POST,
            instance=match,
        )

        if form.is_valid():

            updated_match = form.save()

            messages.success(
                request,
                "Match result updated successfully."
            )

            return redirect(
                "matches_app:competition_season_results",
                competition_season_id=updated_match.competition_season_id,
            )

    else:
        form = MatchResultForm(instance=match)

    context = {
        "match": match,
        "form": form,
        "competition_season": match.competition_season,
    }

    return render(
        request,
        "matches_app/competition_season/match_result_update.html",
        context,
    )