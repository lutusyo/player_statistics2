
from django.contrib import admin

from .models.data_collection import (
    TrainingTopic,
    TrainingObjective,
    CoachingPoint,
    TrainingSession,
    SessionTopic,
    PlayerParticipation,
    PlayerIntervention,
    PlayerInterventionCoachingPoint,
    SessionEvaluation,
)


# ============================================================
# TOPICS, OBJECTIVES AND COACHING POINTS
# ============================================================

@admin.register(TrainingTopic)
class TrainingTopicAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "is_active", "order")
    list_filter = ("category", "is_active")
    search_fields = ("name",)
    list_editable = ("is_active", "order")
    ordering = ("category", "order", "name")


@admin.register(TrainingObjective)
class TrainingObjectiveAdmin(admin.ModelAdmin):
    list_display = ("name", "topic", "is_active", "order")
    list_filter = ("topic", "is_active")
    search_fields = ("name", "topic__name")
    list_editable = ("is_active", "order")


@admin.register(CoachingPoint)
class CoachingPointAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "objective",
        "position",
        "is_active",
        "order",
    )
    list_filter = ("position", "is_active", "objective__topic")
    search_fields = ("name", "objective__name", "objective__topic__name")
    list_editable = ("is_active", "order")


# ============================================================
# SESSION TOPICS
# ============================================================

class SessionTopicInline(admin.TabularInline):
    model = SessionTopic
    extra = 1


# ============================================================
# PLAYER PARTICIPATION
# ============================================================

class PlayerParticipationInline(admin.TabularInline):
    model = PlayerParticipation
    extra = 0
    show_change_link = True
    fields = (
        "player",
        "position",
        "participation",
        "minutes",
        "performance",
    )


# ============================================================
# TRAINING SESSION
# ============================================================

@admin.register(TrainingSession)
class TrainingSessionAdmin(admin.ModelAdmin):
    list_display = (
        "date",
        "age_group",
        "team",
        "coach",
        "training_type",
        "duration_minutes",
        "intensity",
    )
    list_filter = ("date", "age_group", "training_type", "intensity")
    search_fields = ("age_group__name", "team__name", "coach__name")
    date_hierarchy = "date"
    inlines = [SessionTopicInline, PlayerParticipationInline]


@admin.register(SessionTopic)
class SessionTopicAdmin(admin.ModelAdmin):
    list_display = ("session", "topic", "objective", "order")
    list_filter = ("topic", "session__age_group")
    search_fields = ("topic__name", "objective__name")
    autocomplete_fields = ("session", "topic", "objective")


@admin.register(PlayerParticipation)
class PlayerParticipationAdmin(admin.ModelAdmin):
    list_display = (
        "player",
        "session",
        "position",
        "participation",
        "minutes",
        "performance",
    )
    list_filter = (
        "session__date",
        "session__age_group",
        "position",
        "participation",
        "performance",
    )
    search_fields = (
        "player__name",
        "player__second_name",
        "player__surname",
    )
    autocomplete_fields = ("player", "session")


# ============================================================
# PLAYER INTERVENTIONS
# ============================================================

class PlayerInterventionCoachingPointInline(admin.TabularInline):
    model = PlayerInterventionCoachingPoint
    extra = 1
    autocomplete_fields = ("coaching_point",)


@admin.register(PlayerIntervention)
class PlayerInterventionAdmin(admin.ModelAdmin):
    list_display = (
        "player_name",
        "session_date",
        "topic_name",
        "result",
    )
    list_filter = ("result", "session_topic__topic")
    search_fields = (
        "player_participation__player__name",
        "player_participation__player__surname",
        "observation",
    )
    inlines = [PlayerInterventionCoachingPointInline]

    @admin.display(description="Player")
    def player_name(self, obj):
        return obj.player_participation.player.full_name

    @admin.display(description="Session date")
    def session_date(self, obj):
        return obj.player_participation.session.date

    @admin.display(description="Topic")
    def topic_name(self, obj):
        return obj.session_topic.topic.name


@admin.register(PlayerInterventionCoachingPoint)
class PlayerInterventionCoachingPointAdmin(admin.ModelAdmin):
    list_display = ("intervention", "coaching_point", "achieved", "note")
    list_filter = ("achieved", "coaching_point__position")
    search_fields = ("coaching_point__name", "note")


# ============================================================
# SESSION EVALUATION
# ============================================================

@admin.register(SessionEvaluation)
class SessionEvaluationAdmin(admin.ModelAdmin):
    list_display = (
        "session",
        "objective_status",
        "training_quality",
        "updated_at",
    )
    list_filter = ("objective_status", "training_quality")
    search_fields = ("session__age_group__name", "coach_comment")
