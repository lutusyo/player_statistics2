from django.contrib import admin
from .models import Match, PlayerMatchStats, Goal, TeamMatchResult
from .forms import GoalForm


@admin.register(TeamMatchResult)
class TeamMatchResultAdmin(admin.ModelAdmin):
    list_display = ['match', 'our_score', 'opponent_score']


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    form = GoalForm
    list_display = ['match', 'scorer', 'assist_by', 'minute', 'is_own_goal']

class PlayerMatchStatsAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj and obj.player.position != 'Goalkeeper':
            # Hide goalkeeper fields
            for field in [
                'is_goalkeeper', 'saves_success_rate', 'clean_sheets',
                'catches', 'punches', 'drops', 'penalties_saved', 'clearances'
            ]:
                if field in form.base_fields:
                    form.base_fields.pop(field)
        return form

admin.site.register(PlayerMatchStats, PlayerMatchStatsAdmin)
admin.site.register(Match)



