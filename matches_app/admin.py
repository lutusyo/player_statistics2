from django.contrib import admin
from django.utils.html import format_html
from matches_app.models import Country, Region, Venue, Match, Competition


# -------------------------------
# Inline for Regions in Country
# -------------------------------
class RegionInline(admin.TabularInline):
    model = Region
    extra = 1


# -------------------------------
# Country Admin
# -------------------------------
@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    inlines = [RegionInline]


# -------------------------------
# Region Admin
# -------------------------------
@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ("name", "country")
    list_filter = ("country",)
    search_fields = ("name", "country__name")


# -------------------------------
# Venue Admin
# -------------------------------
@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ("name", "region", "get_country")
    list_filter = ("region__country", "region")
    search_fields = ("name", "region__name", "region__country__name")

    def get_country(self, obj):
        return obj.region.country.name if obj.region and obj.region.country else "-"
    get_country.short_description = "Country"


# -------------------------------
# Competition Admin (NEW)
# -------------------------------
@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "logo_preview")
    list_filter = ("type",)
    search_fields = ("name", "type")

    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" width="30" />', obj.logo.url)
        return "-"
    logo_preview.short_description = "Logo"


# -------------------------------
# Match Admin
# -------------------------------
@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = (
        "home_team",
        "away_team",
        "date",
        "competition_logo",
        "competition_name",
        "venue",
        "get_region",
        "get_country",
        "season",
        "age_group",
        "group",
    )

    list_filter = (
        "competition__type",
        "season",
        "age_group",
        "group",
        "venue__region__country",
        "venue__region",
    )

    search_fields = ("home_team__name", "away_team__name", "venue__name")

    # Show region
    def get_region(self, obj):
        return obj.venue.region.name if obj.venue and obj.venue.region else "-"
    get_region.short_description = "Region"

    # Show country
    def get_country(self, obj):
        return (
            obj.venue.region.country.name
            if obj.venue and obj.venue.region and obj.venue.region.country
            else "-"
        )
    get_country.short_description = "Country"

    # Show competition name
    def competition_name(self, obj):
        return obj.competition.name if obj.competition else "-"
    competition_name.short_description = "Competition"

    # Show competition logo
    def competition_logo(self, obj):
        if obj.competition and obj.competition.logo:
            return format_html('<img src="{}" width="30" />', obj.competition.logo.url)
        return "-"
    competition_logo.short_description = "Logo"
