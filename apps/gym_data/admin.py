from django.contrib import admin
from .models import GymSession, GymGroup, GroupExercise


class GroupExerciseInline(admin.TabularInline):
    model = GroupExercise
    extra = 1


@admin.register(GymGroup)
class GymGroupAdmin(admin.ModelAdmin):
    list_display = ["gym_session","group_colour",]
    list_filter = ["group_colour","gym_session__team",]
    filter_horizontal = ["players",]
    inlines = [GroupExerciseInline,]


@admin.register(GymSession)
class GymSessionAdmin(admin.ModelAdmin):
    list_display = ["date","team",]
    list_filter = ["date","team",]
    date_hierarchy = "date"

@admin.register(GroupExercise)
class GroupExerciseAdmin(admin.ModelAdmin):
    list_display = ["exercise","gym_group","weight_kg","sets","reps",]
    list_filter = ["exercise",]