from django.contrib import admin
from matches_app.models import Region, Venue, Match

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display=("name", )
    search_fields = ("name", )

@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display=("name", "region")
    list_filter=("region",)
    search_fields = ("name", )



@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = (
        "home_team",
        "away_team",
        "date",
        "competition_type",
        "venue",
        "get_region",
    )
    list_filter = ("competition_type", "season", "age_group", "venue__region")
    search_fields = ("home_team__name", "away_team__name")

    def get_region(self, obj):
        if obj.venue and obj.venue.region:
            return obj.venue.region.name
        return "-"
    get_region.short_description = "Region"

