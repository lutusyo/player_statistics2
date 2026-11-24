from django.contrib import admin

from .models import (
    Analysis,
    AnalysisPeriod,
    AnalysisTeam,
    AnalysisPeriodTeam,
    AnalysisRun,
)


class AnalysisPeriodInline(admin.TabularInline):
    model = AnalysisPeriod
    extra = 1


@admin.register(Analysis)
class AnalysisAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "analysis_type",
        "comparison_mode",
        "created_by",
        "created_at",
    )

    list_filter = (
        "analysis_type",
        "comparison_mode",
        "created_at",
    )

    search_fields = ("name", "description")

    inlines = [AnalysisPeriodInline]


@admin.register(AnalysisTeam)
class AnalysisTeamAdmin(admin.ModelAdmin):
    list_display = ("analysis", "team")
    list_filter = ("analysis",)


@admin.register(AnalysisPeriodTeam)
class AnalysisPeriodTeamAdmin(admin.ModelAdmin):
    list_display = ("period", "team")
    list_filter = ("period__analysis",)


@admin.register(AnalysisRun)
class AnalysisRunAdmin(admin.ModelAdmin):
    list_display = (
        "analysis",
        "status",
        "generated_by",
        "generated_at",
    )

    list_filter = ("status", "generated_at")
    readonly_fields = ("generated_at",)