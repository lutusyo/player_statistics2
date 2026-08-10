from django.db import models

class ActivityChoices(models.TextChoices):
    MATCH = 'MATCH', 'Match'
    TRAINING = 'TRAINING', 'Training'
    GYME_SESSION = 'GYME SESSION', 'Gyme Session'
    TEAM_VIDEO_SESSION = 'TEAM VIDEO SESSION', 'Team Video Session'
    INDIVIDUAL_VIDEO_SESSION = 'INDIVIDUAL VIDEO SESSION', 'Individual Video Session'

class AgreementChoices(models.TextChoices):
    TRIAL = 'TRIAL', 'Trial'
    SIGNING = 'SIGNING', 'Signing'

class SeasonChoices(models.TextChoices):
    SEASON_2022_2023 = "2022-2023", "2022-2023"
    SEASON_2023_2024 = "2023-2024", "2023-2024"
    SEASON_2024_2025 = "2024-2025", "2024-2025"
    SEASON_2025_2026 = "2025-2026", "2025-2026"

class CompetitionType(models.TextChoices):
    LOCAL_FRIENDLY = 'Local Friendly', 'Local Friendly'
    INTERNATIONAL_FRIENDLY = 'International Friendly', 'International Friendly'
    NBC_YOUTH_LEAGUE = 'NBC Youth League', 'NBC Youth League'
    NBC_PREMIER_LEAGUE = 'NBC Premier League', 'NBC Premier League'
    CAF_CONFEDERATION_CUP = 'CAF Confederation Cup', 'CAF Confederation Cup'
    AZAM_INTERNATIONAL_TALENT_SHOWCASE = 'Azam International Talent Showcase', 'Azam International Talent Showcase'
    NMB_MAPINDUZI_CUP = 'NMB Mapinduzi Cup', 'NMB Mapinduzi Cup'
    TOURNAMENT = 'Tournament', 'Tournament'

# For medical_data app
class VisitType(models.TextChoices):
    REGULAR_CHECKUP = "regular_checkup", "Regular checkup"
    NEW_INJURY = "new_injury", "New injury"

class MainComplaint(models.TextChoices):
    KNEE_PAIN = "knee_pain", "Knee pain"
    ANKLE_PAIN = "ankle_pain", "Ankle pain"
    GROIN_PAIN = "groin_pain", "Groin pain"
    HAMSTRING_PAIN = "hamstring_pain", "Hamstring pain"
    QUADRICEPS_PAIN = "quadriceps_pain", "Quadriceps pain"
    BACK_PAIN = "back_pain", "Back pain"
    NECK_PAIN = "neck_pain", "Neck pain"
    FINGER_PAIN = "finger_pain", "Finger pain"
    HEEL_PAIN = "heel_pain", "Heel pain"
    POST_OPERATIVE = "post_operative", "Post-operative"
    OTHER = "other", "Other"

class BodySide(models.TextChoices):
    LEFT = "left", "Left"
    RIGHT = "right", "Right"
    BOTH = "both", "Both"
    NOT_APPLICABLE = "not_applicable", "Not applicable"

class TrainingStatus(models.TextChoices):
    FULL_TRAINING = "full_training", "Full training"
    MODIFIED_TRAINING = "modified_training", "Modified training"
    REHABILITATION = "rehabilitation", "Individual rehabilitation"
    DID_NOT_TRAIN = "did_not_train", "Did not train"

class InjuryMechanism(models.TextChoices):
    DIRECT_CONTACT = "direct_contact", "Direct contact"
    INDIRECT_CONTACT = "indirect_contact", "Indirect contact"
    MEDICAL_RELATED = "medical_related", "Medical related"

class InjuryStatus(models.TextChoices):
    NEW = "new", "New"
    ONGOING = "ongoing", "Ongoing"
    RECOVERED = "recovered", "Recovered"
    RECURRENT = "recurrent", "Recurrent"

class AvailabilityStatus(models.TextChoices):
    AVAILABLE = "available", "Available"
    RESTRICTED = "restricted", "Available with restrictions"
    NOT_AVAILABLE = "not_available", "Not available"
    REASSESSMENT = "reassessment", "Awaiting reassessment"


class AttachmentType(models.TextChoices):

    MRI = ("mri","MRI")
    XRAY = ("xray","X-Ray")
    ULTRASOUND = ("ultrasound","Ultrasound")
    IMAGE = ("image","Image")
    VIDEO = ("video","Video")
    REPORT = ("report","Medical Report")
    OTHER = ("other","Other")

class Follow_upStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"
    MISSED = "missed", "Missed"


# ---------xxx medical_data pp xxx----------------  #


    