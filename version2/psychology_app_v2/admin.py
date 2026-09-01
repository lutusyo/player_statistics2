from django.contrib import admin
from version1.players_app.models import Player
from version2.psychology_app_v2.models import  Assessment
from version1.players_app.models import AgeGroup


class AssessmentInline(admin.TabularInline):
    model = Assessment
    extra = 0

#@admin.register(Player)
#class PsychologyPlayerAdmin(admin.ModelAdmin):
#    list_display = ('player_name', 'age_group', 'core_character', 'join_date')
#    search_fields = ('player_name',)
#    list_filter = ('age_group', 'core_character')
#    inlines = [AssessmentInline]


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ('player', 'task', 'start_date', 'end_date', 'overall')
    list_filter = ('task',)
    search_fields = ('player__player_name',)


#@admin.register(AgeGroup)
#class AgeGroupAdmin(admin.ModelAdmin):
#    list_display = ('name',)