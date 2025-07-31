# actions_app/admin.py
from django.contrib import admin
from .models import PlayerDetailedAction

@admin.register(PlayerDetailedAction)
class PlayerDetailedActionAdmin(admin.ModelAdmin):
    list_display = ('player', 'match', 'is_our_team', 'created_at')
    list_filter = ('is_our_team', 'match__date')
    search_fields = ('player__name', 'match__opponent')

    fieldsets = (
        ('Player & Match Info', {
            'fields': ('player', 'match', 'is_our_team')
        }),
        ('1. Offensive Actions', {
            'fields': (
                'shots_on_target_inside_box', 'shots_on_target_outside_box',
                'shots_off_target_inside_box', 'shots_off_target_outside_box',
                'successful_cross', 'unsuccessful_cross',
                'missed_chance', 'bad_pass', 'touches_inside_box'
            )
        }),
        ('2. Defensive Actions', {
            'fields': (
                'blocked_shots', 'aerial_duel_won', 'aerial_duel_lost',
                'one_v_one_duel_won', 'one_v_one_duel_lost', 'ball_lost'
            )
        }),
        ('3. Set Pieces', {
            'fields': ('corners',)
        }),
        ('4. Transition', {
            'fields': ('offsides',)
        }),
        ('5. Discipline', {
            'fields': ('fouls_committed', 'fouls_won', 'mistakes')
        }),
        ('6. Goalkeeping', {
            'fields': ('saves', 'punches', 'drops', 'catches', 'penalties_saved')
        }),
        ('7. Other Info', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('created_at',)
