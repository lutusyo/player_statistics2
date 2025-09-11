# lineup_app/utils.py
from .models import MatchLineup

def get_current_on_pitch_players(match, minute=None):
    """
    Returns queryset of MatchLineup rows for players who are on pitch at given minute.
    If minute=None, defaults to 'now' → players with time_in set and time_out still null.
    """
    qs = MatchLineup.objects.filter(match=match)

    if minute is None:
        # Active now = has entered (time_in not null), and has not left yet (time_out null)
        qs = qs.filter(time_in__isnull=False).filter(time_out__isnull=True)
    else:
        qs = qs.filter(time_in__lte=minute).filter(models.Q(time_out__isnull=True) | models.Q(time_out__gt=minute))

    return qs.select_related("player", "team")
