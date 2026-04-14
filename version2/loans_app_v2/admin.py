from django.contrib import admin
from .models import LoanedPlayer, LoanDailyEntry


# =========================
# INLINE (DAILY ENTRIES)
# =========================
class LoanDailyEntryInline(admin.TabularInline):
    model = LoanDailyEntry
    extra = 0


# =========================
# LOANED PLAYER ADMIN
# =========================
@admin.register(LoanedPlayer)
class LoanedPlayerAdmin(admin.ModelAdmin):

    inlines = [LoanDailyEntryInline]

    list_per_page = 20

    list_display = (
        "full_name",
        "position",
        "loan_club",
        "loan_start_date",
        "loan_end_date",
        "is_active",
    )

    list_filter = (
        "position",
        "loan_club",
        "is_active",
    )

    search_fields = (
        "player__name",
        "player__surname",
        "player__jina_maarufu",
    )

    ordering = ("player__name",)

    readonly_fields = ("created_at",)

    fieldsets = (
        ("Player Info", {
            "fields": (
                "player",
                "date_of_birth",
                "position",
                "role",
                "preferred_foot",
            )
        }),

        ("Physical Info", {
            "fields": (
                "height_cm",
                "weight_kg",
                "jersey_number",
            )
        }),

        ("Contact", {
            "fields": ("phone_number",)
        }),

        ("Loan Info", {
            "fields": (
                "loan_club",
                "loan_start_date",
                "loan_end_date",
                "is_active",
            )
        }),

        ("Media", {
            "fields": ("photo",)
        }),

        ("System", {
            "fields": ("created_at",)
        }),
    )


# =========================
# DAILY ENTRY ADMIN
# =========================
@admin.register(LoanDailyEntry)
class LoanDailyEntryAdmin(admin.ModelAdmin):

    list_display = (
        "player",
        "date",
        "day_type",
        "minutes_played",
        "goals",
        "assists",
        "yellow_cards",
        "red_cards",
    )

    list_filter = (
        "day_type",
        "competition_type",
        "team_side",
        "date",
    )

    search_fields = (
        "player__player__name",
        "player__player__surname",
    )

    ordering = ("-date",)

    readonly_fields = ("created_at",)

    fieldsets = (
        ("Basic Info", {
            "fields": (
                "player",
                "date",
                "day_type",
            )
        }),

        ("Training", {
            "fields": ("training_minutes",)
        }),

        ("Match Info", {
            "fields": (
                "competition_type",
                "competition_name",
                "home_team",
                "away_team",
                "home_score",
                "away_score",
                "team_side",
            )
        }),

        ("Performance", {
            "fields": (
                "appearance",
                "started",
                "minutes_played",
                "goals",
                "assists",
                "pre_assists",
            )
        }),

        ("Discipline", {
            "fields": (
                "yellow_cards",
                "red_cards",
                "clean_sheet",
            )
        }),

        ("System", {
            "fields": ("created_at",)
        }),
    )