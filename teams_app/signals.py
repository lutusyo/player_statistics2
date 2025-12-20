from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import date

from teams_app.models import Team
from players_app.models import Player


@receiver(post_save, sender=Team, dispatch_uid="create_default_players_once")
def create_default_players(sender, instance, created, **kwargs):
    if not created:
        return

    # 🚨 SAFETY CHECK
    if Player.objects.filter(team=instance).exists():
        return

    positions = [
        "Goalkeeper",
        "Defender",
        "Defender",
        "Defender",
        "Defender",
        "Midfielder",
        "Winger",
        "Midfielder",
        "Forward",
        "Forward",
        "Winger",
    ]

    players = []

    for i in range(11):
        players.append(
            Player(
                name=str(i + 1),
                second_name="",
                surname="",
                team=instance,
                jersey_number=i + 1,
                position=positions[i],
                birthdate=date.today(),
                age_group=instance.age_group,
                is_active=True,
            )
        )

    Player.objects.bulk_create(players)
