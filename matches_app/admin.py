from django.contrib import admin
from matches_app.models import Country, Region, Venue, Match


class RegionInline(admin.TabularInline):
    model = Region
    extra = 1

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    inlines = [RegionInline]


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ("name", "country")
    list_filter = ("country",)
    search_fields = ("name", "country__name")

@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ("name", "region", "get_country")
    list_filter = ("region__country", "region")
    search_fields = ("name", "region__name", "region__country__name")

    def get_country(self, obj):
        return obj.region.country.name if obj.region and obj.region.country else "-"
    get_country.short_description = "Country"






@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ( "home_team", "away_team", "date", "competition_type", "venue", "get_region", "get_country", )
    list_filter = ("competition_type", "season", "age_group", "venue__region__country", "venue__region", )
    search_fields = ("home_team__name", "away_team__name", "venue__name", )

    def get_region(self, obj):
        return obj.venue.region.name if obj.venue and obj.venue.region else "-"
    get_region.short_description = "Region"

    def get_country(self, obj):
        return (
            obj.venue.region.country.name
            if obj.venue and obj.venue.region and obj.venue.region.country
            else "-")
    get_country.short_description = "Country"


