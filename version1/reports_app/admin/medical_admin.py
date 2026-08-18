from django.contrib import admin

from version1.reports_app.models.previous_models import (
    Medical,
    Transition,
    Scouting,
    Performance,
    IndividualActionPlan,
    Mesocycle,
    FitnessPlan,
)


@admin.register(Medical)
class MedicalAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "status",
        "injury_or_illness",
        "date",
        "squad",
    )

    list_filter = (
        "status",
        "squad",
    )

    search_fields = (
        "name__first_name",
        "name__last_name",
        "injury_or_illness",
    )


@admin.register(Transition)
class TransitionAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "activity",
        "played_for",
        "squad",
        "date",
    )

    list_filter = (
        "activity",
        "squad",
    )

    search_fields = (
        "name__first_name",
        "name__last_name",
        "played_for",
    )


@admin.register(Scouting)
class ScoutingAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "pos",
        "agreement",
        "squad",
        "date",
    )

    list_filter = (
        "agreement",
        "squad",
    )

    search_fields = (
        "name",
        "pos",
    )


@admin.register(Performance)
class PerformanceAdmin(admin.ModelAdmin):

    list_display = (
        "squad",
        "activity",
        "date",
    )

    list_filter = (
        "activity",
        "squad",
    )

    search_fields = (
        "squad__name",
    )


@admin.register(IndividualActionPlan)
class IndividualActionPlanAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "category",
        "responsibility",
        "status",
        "date",
        "squad",
    )

    list_filter = (
        "category",
        "status",
        "squad",
    )

    search_fields = (
        "name__first_name",
        "name__last_name",
        "responsibility",
    )


@admin.register(Mesocycle)
class MesocycleAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "team",
        "start_date",
        "end_date",
        "uploaded_at",
    )

    list_filter = (
        "team",
    )

    search_fields = (
        "title",
        "team__name",
    )


@admin.register(FitnessPlan)
class FitnessPlanAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "team",
        "start_date",
        "end_date",
        "uploaded_at",
    )

    list_filter = (
        "team",
    )

    search_fields = (
        "title",
        "team__name",
    )