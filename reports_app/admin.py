from django.contrib import admin
from django.db import models
from .models import (
    Medical,
    Transition,
    Scouting,
    Performance,
    IndividualActionPlan,
    Mesocycle,
    FitnessPlan,
    Result,
    TrainingMinutes,
    PlayerTrainingMinutes
)


@admin.register(Medical)
class MedicalAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'injury_or_illness', 'date', 'squad')
    list_filter = ('status', 'squad')
    search_fields = ('name__first_name', 'name__last_name', 'injury_or_illness')


@admin.register(Transition)
class TransitionAdmin(admin.ModelAdmin):
    list_display = ('name', 'activity', 'played_for', 'squad', 'date')
    list_filter = ('activity', 'squad')
    search_fields = ('name__first_name', 'name__last_name', 'played_for')


@admin.register(Scouting)
class ScoutingAdmin(admin.ModelAdmin):
    list_display = ('name', 'pos', 'agreement', 'squad', 'date')
    list_filter = ('agreement', 'squad')
    search_fields = ('name', 'pos')


@admin.register(Performance)
class PerformanceAdmin(admin.ModelAdmin):
    list_display = ('squad', 'activity', 'date')
    list_filter = ('activity', 'squad')
    search_fields = ('squad__name',)


@admin.register(IndividualActionPlan)
class IndividualActionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'responsibility', 'status', 'date', 'squad')
    list_filter = ('category', 'status', 'squad')
    search_fields = ('name__first_name', 'name__last_name', 'responsibility')


@admin.register(Mesocycle)
class MesocycleAdmin(admin.ModelAdmin):
    list_display = ('title', 'team', 'start_date', 'end_date', 'uploaded_at')
    list_filter = ('team',)
    search_fields = ('title', 'team__name')


@admin.register(FitnessPlan)
class FitnessPlanAdmin(admin.ModelAdmin):
    list_display = ('team', 'focus_area', 'week_number', 'date')
    list_filter = ('team', 'week_number')
    search_fields = ('team__name', 'focus_area')


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('date', 'competition_type', 'venue', 'home_team', 'home_score', 'away_team', 'away_score', 'our_team', 'result')
    list_filter = ('competition_type', 'home_team', 'away_team', 'our_team', 'result')
    search_fields = ('home_team__name', 'away_team__name', 'competition_type', 'venue')
    date_hierarchy = 'date'
    
    # Make goal scorers a bigger text area
    fieldsets = (
        (None, {
            'fields': (
                'date', 'venue', 'competition_type', 'home_team', 'away_team', 
                ('home_score', 'away_score'), 'our_team', 'goal_scorers', 'notes'
            ),
        }),
    )
    formfield_overrides = {
        # Optional: make goal_scorers textarea larger
        models.TextField: {'widget': admin.widgets.AdminTextareaWidget(attrs={'rows': 4, 'cols': 50})},
    }


@admin.register(TrainingMinutes)
class TrainingMinutesAdmin(admin.ModelAdmin):
    list_display = ('date', 'team', 'total_minutes', 'physical_minutes', 'tactical_minutes', 'technical_minutes', 'recovery_minutes')
    list_filter = ('team', 'date')
    search_fields = ('team__name',)

@admin.register(PlayerTrainingMinutes)
class PlayerTrainingMinutesAdmin(admin.ModelAdmin):
    list_display = ('player', 'training_session', 'minutes')
    list_filter = ('player__team', 'training_session__date')
    search_fields = ('player__first_name', 'player__last_name')
