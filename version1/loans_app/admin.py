from django.contrib import admin
from .models import LoanedPlayer, LoanDailyEntry


# =========================
# INLINE DAILY ENTRIES
# =========================
class LoanDailyEntryInline(admin.TabularInline):
    model = LoanDailyEntry
    extra = 0
    ordering = ("-date",)
    fields = (
        "date",
        "day_type",
        "competition_name",
        "home_team",
        "away_team",
        "home_score",
        "away_score",
        "appearance",
        "minutes_played",
        "goals",
        "assists",
    )


# =========================
# PLAYER ADMIN
# =========================
@admin.register(LoanedPlayer)
class LoanedPlayerAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "position",
        "loan_club",
        "loan_club_country",
        "is_active",
    )
    list_filter = (
        "position",
        "loan_club_country",
        "is_active",
    )
    search_fields = (
        "full_name",
        "loan_club",
    )
    readonly_fields = ("created_at",)

    inlines = [LoanDailyEntryInline]


# =========================
# DAILY ENTRY ADMIN
# =========================
@admin.register(LoanDailyEntry)
class LoanDailyEntryAdmin(admin.ModelAdmin):

    list_display = (
        "player",
        "date",
        "day_type",
        "competition_name",
        "display_match",
        "appearance",
        "minutes_played",
        "goals",
        "assists",
        "yellow_cards",
        "red_cards",
    )

    list_filter = (
        "day_type",
        "competition_type",
        "competition_name",
        "appearance",
    )

    search_fields = (
        "player__full_name",
        "home_team",
        "away_team",
    )

    ordering = ("-date",)

    # 🔥 Custom column for match display
    def display_match(self, obj):
        if obj.day_type == "match":
            return f"{obj.home_team} {obj.home_score}-{obj.away_score} {obj.away_team}"
        return "Training"
    
    display_match.short_description = "Match"