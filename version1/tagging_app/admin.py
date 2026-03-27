#tagging_app/admin.py
from django.contrib import admin
from django.utils.html import format_html

from version1.tagging_app.models import AttemptToGoal, PassEvent



@admin.register(AttemptToGoal)
class AttemptToGoalAdmin(admin.ModelAdmin):
    list_display = ('player', 'match', 'team', 'minute', 'second', 'outcome', 'video_preview' )
    list_filter = ('match', 'team', 'outcome', 'delivery_type')
    search_fields = ('player__name',)
    readonly_fields = ('video_preview',)
    fields = (
        'match', 'team', 'player',
        'minute', 'second',
        'delivery_type', 'outcome',
        'body_part', 'location_tag',
        'video_clip', 'video_preview', 'thumbnail',
        'assist_by', 'pre_assist_by',
        'is_opponent', 'is_own_goal', 'own_goal_for',
        'x', 'y'
    )

    def video_preview(self, obj):
        if obj.video_clip:
            return format_html(
                '<video width="200" controls>'
                '<source src="{}" type="video/mp4">'
                'Your browser does not support the video tag.'
               '</video>',
               obj.video_clip.url
            )
        return "No video"

    video_preview.short_description = 'Preview'


@admin.register(PassEvent)
class PassEventAdmin(admin.ModelAdmin):
    list_display = ('from_player', 'to_player', 'match', 'minute', 'second', 'is_successful')
    list_filter = ('match', 'is_successful')


