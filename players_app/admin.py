from django.contrib import admin

from .models import Player, PlayerCareerStage


class PlayerCareerStageInline(admin.TabularInline):
    model = PlayerCareerStage
    extra = 1

class PlayerAdmin(admin.ModelAdmin):
    inlines = [PlayerCareerStageInline]


admin.site.register(Player, PlayerAdmin)

