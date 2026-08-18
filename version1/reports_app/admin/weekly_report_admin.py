from django.contrib import admin

from version1.reports_app.models import (
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
    list_display = ["report"]


@admin.register(AfterActionReview)
class AfterActionReviewAdmin(admin.ModelAdmin):
    list_display = ["report"]



@admin.register(SquadStatus)
class SquadStatusAdmin(admin.ModelAdmin):
    list_display = [
        "report",
        "available_players",
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