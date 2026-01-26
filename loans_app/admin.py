from django.contrib import admin
from .models import LoanedPlayer, LoanDailyEntry

class LoanDailyEntryInline(admin.TabularInline):
    model = LoanDailyEntry
    extra = 0
    ordering = ("-date",)


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


@admin.register(LoanDailyEntry)
class LoanDailyEntryAdmin(admin.ModelAdmin):
    list_display = (
        "player",
        "date",
        "day_type",
        "match_type",
        "minutes_played",
        "goals",
        "assists",
        "yellow_cards",
        "red_cards",
    )
    list_filter = (
        "day_type",
        "match_type",
    )
    search_fields = (
        "player__full_name",
    )
    ordering = ("-date",)
