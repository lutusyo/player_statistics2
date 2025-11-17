from django.contrib import admin
from perfomance_rating_app.models import PerformanceRating, StaffPlayerRating, RatingToken


@admin.register(PerformanceRating)
class PerformanceRatingAdmin(admin.ModelAdmin):
    list_display = (
        "player",
        "match",
        "attacking",
        "creativity",
        "defending",
        "tactical",
        "technical",
        "discipline",
        "is_computed",
        "is_manual",
        "created_at",
        "overall_value",
    )
    list_filter = ("is_computed", "is_manual", "created_at", "match")
    search_fields = ("player__name", "match__opponent", "match__date")
    autocomplete_fields = ("player", "match")

    def overall_value(self, obj):
        return obj.overall()
    overall_value.short_description = "Overall"


@admin.register(StaffPlayerRating)
class StaffPlayerRatingAdmin(admin.ModelAdmin):
    list_display = ("staff", "player", "match", "rating", "submitted_at")
    list_filter = ("staff", "match", "submitted_at")
    search_fields = ("staff__name", "player__name", "match__opponent")
    autocomplete_fields = ("staff", "player", "match")


@admin.register(RatingToken)
class RatingTokenAdmin(admin.ModelAdmin):
    list_display = ("staff", "match", "token", "used", "created_at", "expires_at", "used_at")
    list_filter = ("used", "created_at", "expires_at")
    search_fields = ("staff__name", "match__opponent", "token")
    autocomplete_fields = ("staff", "match")
