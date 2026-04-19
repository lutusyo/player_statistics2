from django.db import models

class MatchPeriod(models.TextChoices):
    FIRST_HALF = "1H", "First Half"
    SECOND_HALF = "2H", "Second Half"
    EXTRA_TIME_FIRST = "ET1", "Extra Time 1st Half"
    EXTRA_TIME_SECOND = "ET2", "Extra Time 2nd Half"
    PENALTIES = "PEN", "Penalty Shootout"

# GENERAL EVENT TYPES
class EventType(models.TextChoices):
    PASS = "pass", "Pass"
    SHOT = "shot", "Shot"
    FOUL = "foul", "Foul"
    DRIBBLE = "dribble", "Dribble"
    GK_DISTRIBUTION = "gk_distribution", "GK Distribution"
    DEFENSIVE_ACTION = "defensive_action", "Defensive Action"


# BALL ACTIONS (from v2 improved)
BALL_ACTION_CHOICES = [

    ("HIGH_BALL", "High Ball"),  # aerial duels

    ("GROUND_PASS", "Ground Pass"),
    ("LONG_PASS", "Long Pass"),

    ("GOAL_KICK", "Goal Kick"),
    ("CLEARANCE", "Clearance"),
    ("CROSS", "Cross"),
    ("THROW_IN", "Throw In"),

    ("DRIBBLE", "Dribble"),
    ("BALL_SHIELDING", "Ball Shielding"),

    ("INTERCEPTION", "Interception"),
    ("TACKLE", "Tackle"),

    ("FOUL", "Foul"),
    ("OFFSIDE", "Offside"),
]

# FOUL OUTCOME
FOUL_OUTCOME = [
    ("NO_CARD", "No Card"),
    ("YELLOW_CARD", "Yellow Card"),
    ("RED_CARD", "Red Card"),
]


# DELIVERY TYPE (Shots / Crosses)
class DeliveryTypeChoices(models.TextChoices):
    PASS = 'Pass', 'Pass'
    CROSS = 'Cross', 'Cross'
    LOOSE_BALL = 'Loose Ball', 'Loose Ball'
    CORNER = 'Corner', 'Corner'
    FREE_KICK = 'Free Kick', 'Free Kick'
    REBOUND = 'Rebound', 'Rebound'

# SHOT OUTCOME
class OutcomeChoices(models.TextChoices):
    OFF_TARGET = 'Off Target', 'Off Target'
    ON_TARGET_SAVED = 'On Target Saved', 'On Target Saved'
    ON_TARGET_GOAL = 'On Target Goal', 'On Target Goal'
    BLOCKED = 'Blocked', 'Blocked'
    PLAYER_ERROR = 'Player Error', 'Player Error'
    OWN_GOAL = 'Own Goal', 'Own Goal'
    POST = 'Post', 'Post'
    CROSSBAR = 'Crossbar', 'Crossbar'


# SHOT LOCATION
class LocationChoices(models.TextChoices):
    # Outside box
    OUTSIDE_BOX_LEFT = "Outside box left", "Outside box left"
    OUTSIDE_BOX_CENTER = "Outside box center", "Outside box center"
    OUTSIDE_BOX_RIGHT = "Outside box right", "Outside box right"

    # Inside box
    INSIDE_BOX_LEFT = "Inside box left", "Inside box left"
    INSIDE_BOX_CENTER = "Inside box center", "Inside box center"
    INSIDE_BOX_RIGHT = "Inside box right", "Inside box right"

    # Six-yard box
    SIX_YARD_LEFT = "Six-yard box left", "Six-yard box left"
    SIX_YARD_CENTER = "Six-yard box center", "Six-yard box center"
    SIX_YARD_RIGHT = "Six-yard box right", "Six-yard box right"

    # Specific
    PENALTY_SPOT = "Penalty spot", "Penalty spot"
    LONG_RANGE = "Long Range", "Long Range"
    OTHER = "Other", "Other"


# BODY PART
class BodyPartChoices(models.TextChoices):
    RIGHT_FOOT = 'Right Foot', 'Right Foot'
    LEFT_FOOT = 'Left Foot', 'Left Foot'
    HEADER = 'Header', 'Header'
    OTHER = 'Other', 'Other'

# GOALKEEPER DISTRIBUTION
class GKDistributionMethod(models.TextChoices):
    FEET = 'from_feet', 'From Feet'
    HANDS = 'from_hands', 'From Hands'
    THROW = 'throw', 'Throw'


class GKDistributionDetail(models.TextChoices):
    # Feet
    PLAY_ONTO = 'play_onto', 'Play Onto'
    PLAY_INTO = 'play_into', 'Play Into'
    PLAY_AROUND = 'play_around', 'Play Around'
    PLAY_BEYOND = 'play_beyond', 'Play Beyond'
    OTHER_FEET = 'other_feet', 'Other (Feet)'

    # Kicks
    SIDE_KICK = 'side_kick', 'Side Kick'
    DROP_KICK = 'drop_kick', 'Drop Kick'

    # Throws
    OVER_ARM = 'over_arm', 'Over Arm'
    UNDER_ARM = 'under_arm', 'Under Arm'
    SIDE_ARM = 'side_arm', 'Side Arm'
    CHEST_PASS = 'chest_pass', 'Chest Pass'



    




