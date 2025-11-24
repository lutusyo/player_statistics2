from django.contrib import admin
from players_app.models import Player, PlayerCareerStage, PlayerMeasurement

# Inline for Career Stages
class PlayerCareerStageInline(admin.TabularInline):
    model = PlayerCareerStage
    extra = 1

# Inline for Measurements
class PlayerMeasurementInline(admin.TabularInline):
    model = PlayerMeasurement
    extra = 1
    readonly_fields = ('date_measured',)  # you can’t edit the measurement date

# Player Admin
@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ("name", "jersey_number", "team", "current_bmi")
    search_fields = ("name",)
    inlines = [PlayerCareerStageInline, PlayerMeasurementInline]

    def current_bmi(self, obj):
        return obj.bmi
    current_bmi.short_description = "BMI"
