from django.contrib import admin
from players_app.models import Player, PlayerCareerStage


class PlayerCareerStageInline(admin.TabularInline):
    model = PlayerCareerStage
    extra = 1


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ("name", "jersey_number", "team")
    search_fields = ("name",)
    inlines = [PlayerCareerStageInline]
