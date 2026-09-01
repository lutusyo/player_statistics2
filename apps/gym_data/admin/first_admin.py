from django.contrib import admin

from ..models import (
    GymType,
    ExerciseCategory,
    Exercise,
    GymSession,
    GymGroup,
    GroupExercise,
)


@admin.register(GymType)
class GymTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(ExerciseCategory)
class ExerciseCategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ("name", "category")
    list_filter = ("category",)
    search_fields = ("name",)


@admin.register(GymSession)
class GymSessionAdmin(admin.ModelAdmin):
    list_display = ("date", "team")
    list_filter = ("team", "date")


@admin.register(GymGroup)
class GymGroupAdmin(admin.ModelAdmin):
    list_display = (
        "gym_session",
        "gym_type",
    )

    list_filter = (
        "gym_type",
        "gym_session__team",
    )


@admin.register(GroupExercise)
class GroupExerciseAdmin(admin.ModelAdmin):
    list_display = (
        "gym_group",
        "exercise",
        "weight_kg",
        "sets",
        "reps",
    )

    list_filter = (
        "exercise__category",
        "exercise",
    )