from django.contrib import admin
from django import forms
from django.shortcuts import render, redirect
from django.urls import path, reverse
from django.utils.html import format_html
from django.contrib import messages
from django.forms import modelformset_factory
from lineup_app.models import Match, MatchLineup, Substitution
from lineup_app.forms import MatchLineupForm
from players_app.models import Player

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

        existing_lineups = MatchLineup.objects.filter(match=match)
        existing_players = existing_lineups.values_list('player_id', flat=True)
        remaining_players = players.exclude(id__in=existing_players)

        # Create initial data for players not already in lineup
        extra_forms = [{
            'player': player,
            'time_in': 0,  # Changed from 'time_entered' to 'time_in' and default 0
            'pod_number': 'Demo 2',
        } for player in remaining_players]

        LineupFormSet = modelformset_factory(
            MatchLineup,
            form=MatchLineupBulkForm,
            extra=len(extra_forms),
            can_delete=True
        )

        if request.method == 'POST':
            formset = LineupFormSet(
                request.POST,
                queryset=existing_lineups,
                initial=extra_forms,
                form_kwargs={'match': match}
            )

            if formset.is_valid():
                # Assign match & team AFTER validation, safe to use cleaned_data
                for form in formset.forms:
                    if form.cleaned_data and form.cleaned_data.get('player'):
                        if form.instance.pk is None:  # New record
                            form.instance.match = match

                        player = form.cleaned_data['player']
                        age_group = player.age_group
                        match_teams = [match.home_team, match.away_team]
                        teams_for_age_group = age_group.team_set.all()

                        # Find the matching team from the match's teams
                        matched_teams = [team for team in match_teams if team in teams_for_age_group]
                        form.instance.team = matched_teams[0] if matched_teams else None

                formset.save()
                messages.success(request, "Lineup saved successfully.")
                return redirect('admin:matches_app_match_changelist')
            else:
                for form in formset:
                    if form.errors:
                        print(form.errors)
                messages.error(request, "There were errors in the form.")
        else:
            formset = LineupFormSet(
                queryset=existing_lineups,
                initial=extra_forms,
                form_kwargs={'match': match}
            )

        return render(request, 'admin/matches_app/bulk_lineup_form.html', {
            'formset': formset,
            'match': match,
        })


### Register Models ###
admin.site.register(Match, MatchAdmin)


