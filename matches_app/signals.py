from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Goal, PlayerMatchStats

@receiver([post_save, post_delete], sender=Goal)
def update_player_match_stats(sender, instance, **kwargs):
    match = instance.match

    players_in_match = PlayerMatchStats.objects.filter(match=match)

    for stats in players_in_match:
        player = stats.player
        stats.goals = Goal.objects.filter(match=match, scorer=player, is_own_goal=False).count()
        stats.assists = Goal.objects.filter(match=match, assist_by=player).count()
        stats.save()
