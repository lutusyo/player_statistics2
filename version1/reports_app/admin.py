from django.contrib import admin
from django.db import models
from version1.players_app.models import Player

from version1.reports_app.models.previous_models import (
    Medical,
    Transition,
    Scouting,
    Performance,
    IndividualActionPlan,
    Mesocycle,
    FitnessPlan,
    Result,
    TrainingMinutes,
    PlayerTrainingMinutes,
    TrainingAbsence
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
    list_display = ('title', 'team', 'start_date', 'end_date', 'uploaded_at')
    list_filter = ('team',)
    search_fields = ('title', 'team__name')


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


class PlayerTrainingMinutesInline(admin.TabularInline):
    model = PlayerTrainingMinutes
    extra = 0

    fields = (
        'player',
        'trained_with_team',
        'minutes',
    )

    autocomplete_fields = (
        'player',
        'trained_with_team',
    )


class TrainingAbsenceInline(admin.TabularInline):
    model = TrainingAbsence
    extra = 0
    autocomplete_fields = ['player']

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == "player":
            obj_id = request.resolver_match.kwargs.get("object_id")
            if obj_id:
                training = TrainingMinutes.objects.get(id=obj_id)
                kwargs["queryset"] = Player.objects.filter(team=training.team)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
@admin.register(TrainingAbsence)
class TrainingAbsenceAdmin(admin.ModelAdmin):

    list_display = (
        'player',
        'training_session',
        'reason',
    )

    list_filter = (
        'reason',
        'training_session__team',
        'training_session__session',
        'training_session__date',
    )

    search_fields = (
        'player__first_name',
        'player__last_name',
    )


@admin.register(TrainingMinutes)
class TrainingMinutesAdmin(admin.ModelAdmin):
    list_display = (
        'date',
        'team',
        'session',
        'total_minutes',
    )

    list_filter = ('team','session','date',)
    search_fields = ('team__name',)
    ordering = ('-date','team','session',)

    inlines = [
        PlayerTrainingMinutesInline,
        TrainingAbsenceInline,
    ]


@admin.register(PlayerTrainingMinutes)
class PlayerTrainingMinutesAdmin(admin.ModelAdmin):

    list_display = ('player','training_session','trained_with_team','minutes',)
    list_filter = ('trained_with_team','training_session__team','training_session__session','training_session__date',)
    search_fields = ('player__first_name','player__last_name',)
    autocomplete_fields = ('player','training_session','trained_with_team',)


    ##################################################################################################################

    from django.contrib import admin

from .models import (
    WeeklyReport,
    BeforeActionReview,
    AfterActionReview,
    SquadStatus,
    DiscussionPoint,
    DecisionPoint,
)


class BeforeActionReviewInline(admin.StackedInline):
    model = BeforeActionReview
    extra = 0
    max_num = 1


class AfterActionReviewInline(admin.StackedInline):
    model = AfterActionReview
    extra = 0
    max_num = 1


class SquadStatusInline(admin.StackedInline):
    model = SquadStatus
    extra = 0
    max_num = 1


class DiscussionPointInline(admin.TabularInline):
    model = DiscussionPoint
    extra = 1


class DecisionPointInline(admin.TabularInline):
    model = DecisionPoint
    extra = 1


@admin.register(WeeklyReport)
class WeeklyReportAdmin(admin.ModelAdmin):

    list_display = [
        "team",
        "season",
        "week",
        "coach",
        "week_start",
        "week_end",
        "status",
    ]

    list_filter = [
        "team",
        "season",
        "status",
    ]

    search_fields = [
        "team__name",
        "coach__username",
        "title",
    ]

    readonly_fields = [
        "created_at",
        "updated_at",
        "submitted_at",
        "approved_at",
    ]

    inlines = [
        BeforeActionReviewInline,
        AfterActionReviewInline,
        SquadStatusInline,
        DiscussionPointInline,
        DecisionPointInline,
    ]


@admin.register(BeforeActionReview)
class BeforeActionReviewAdmin(admin.ModelAdmin):
    list_display = [
        "report",
    ]


@admin.register(AfterActionReview)
class AfterActionReviewAdmin(admin.ModelAdmin):
    list_display = [
        "report",
    ]


@admin.register(SquadStatus)
class SquadStatusAdmin(admin.ModelAdmin):
    list_display = [
        "report",
        "available_players",
      #  "injured_players",
        "unavailable_players",
    ]


@admin.register(DiscussionPoint)
class DiscussionPointAdmin(admin.ModelAdmin):
    list_display = [
        "report",
        "category",
        "point",
        "order",
    ]

    list_filter = [
        "category",
    ]


@admin.register(DecisionPoint)
class DecisionPointAdmin(admin.ModelAdmin):
    list_display = [
        "report",
        "decision",
        "responsible",
        "deadline",
        "completed",
    ]

    list_filter = [
        "completed",
    ]