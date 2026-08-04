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

    