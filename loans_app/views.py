from django.shortcuts import render, get_object_or_404
from loans_app.models import LoanedPlayer, LoanDailyEntry

def player_list_view(request):
    players = LoanedPlayer.objects.all().order_by("full_name")
    # or: LoanedPlayer.objects.filter(is_active=True)

    context = {"players": players}

    return render(request, "loans_app/player_list.html", context)


def player_detail_view(request, player_id):
    player = get_object_or_404(LoanedPlayer, id=player_id)

    daily_entries = player.daily_entries.all()

    context = {
        "player": player,
        "daily_entries": daily_entries,
    }
    return render(request, "loans_app/player_detail.html", context)
