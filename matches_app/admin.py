from django.contrib import admin
from django import forms
from django.shortcuts import render, redirect
from django.urls import path, reverse
from django.utils.html import format_html
from django.contrib import messages
from django.forms import modelformset_factory

from .models import Match, MatchLineup, Substitution
from .forms import MatchLineupForm
from players_app.models import Player


### Bulk Lineup Form ###
class MatchLineupBulkForm(forms.ModelForm):
    class Meta:
        model = MatchLineup
        fields = ['player', 'position', 'pod_number', 'is_starting', 'time_entered']

    def __init__(self, *args, **kwargs):
        match = kwargs.pop('match', None)
        super().__init__(*args, **kwargs)
        if match:
            self.fields['time_entered'].initial = match.time
            # Filter players by age groups of both teams
            home_age_group = match.home_team.age_group
            away_age_group = match.away_team.age_group
            self.fields['player'].queryset = Player.objects.filter(age_group__in=[home_age_group, away_age_group])


### Match Admin with Create Lineup Button ###
class MatchAdmin(admin.ModelAdmin):
    list_display = ['home_team', 'away_team', 'date', 'competition_type', 'create_lineup_link']

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:match_id>/create-lineup/', self.admin_site.admin_view(self.create_lineup), name='create_lineup'),
        ]
        return custom_urls + urls

    def create_lineup_link(self, obj):
        url = reverse('admin:create_lineup', args=[obj.id])
        return format_html('<a class="button" href="{}">Create Lineup</a>', url)
    create_lineup_link.short_description = 'Lineup'

    def create_lineup(self, request, match_id):
        match = Match.objects.get(id=match_id)

        home_age_group = match.home_team.age_group
        away_age_group = match.away_team.age_group
        players = Player.objects.filter(age_group__in=[home_age_group, away_age_group])

        LineupFormSet = modelformset_factory(
            MatchLineup,
            form=MatchLineupBulkForm,
            extra=len(players),  # ✅ Generate 1 form per player
            can_delete=True
        )

        initial_data = []
        for player in players:
            initial_data.append({
                'player': player,
                'time_entered': match.time,
            })

        if request.method == 'POST':
            formset = LineupFormSet(request.POST, queryset=MatchLineup.objects.none(), form_kwargs={'match': match})
            if formset.is_valid():
                for form in formset.forms:
                    instance = form.save(commit=False)
                    instance.match = match
                    instance.team = instance.player.age_group.team_set.first() if instance.player.age_group else None

                    role = request.POST.get(f"{form.prefix}-role")
                    if role == 'starter':
                        instance.is_starting = True
                        instance.time_entered = None
                    elif role == 'sub':
                        instance.is_starting = False
                        instance.time_entered = match.time
                    else:
                        instance.is_starting = False
                        instance.time_entered = None

                    instance.save()

                messages.success(request, "Lineup saved successfully.")
                return redirect('admin:matches_app_match_changelist')
            else:
                messages.error(request, "There were errors in the form.")
        else:
            formset = LineupFormSet(queryset=MatchLineup.objects.none(), initial=initial_data, form_kwargs={'match': match})

        return render(request, 'admin/matches_app/bulk_lineup_form.html', {
            'formset': formset,
            'match': match,
        })


### Lineup Admin ###
class MatchLineupAdmin(admin.ModelAdmin):
    form = MatchLineupForm
    list_display = ['match', 'player', 'team', 'position', 'is_starting']
    list_filter = ['match', 'team', 'is_starting']
    search_fields = ['player__name']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('match', 'player', 'team')


### Register Models ###
admin.site.register(Match, MatchAdmin)
admin.site.register(MatchLineup, MatchLineupAdmin)
admin.site.register(Substitution)
