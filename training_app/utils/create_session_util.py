from training_app.models import TrainingSession, PlayerAttendance
from players_app.models import Player


def create_training_session(duration, training_types, player_ids):
    """
    Create a TrainingSession and PlayerAttendance records.

    Args:
        duration (int or str): Training duration in minutes.
        training_types (list[str]): List of training type strings.
        player_ids (list[str] or list[int]): List of player IDs who attended.

    Returns:
        TrainingSession: The created session instance.
    """

    training_types_str = ','.join(training_types)

    session = TrainingSession.objects.create(
        duration_minutes=duration,
        training_types=training_types_str
    )

    all_players = Player.objects.all()

    for player in all_players:
        attended = str(player.id) in player_ids
        PlayerAttendance.objects.create(session=session, player=player, attended=attended)

    return session
