from django.contrib import admin
from .models import Player, Match, PlayerMatchStats

admin.site.register(Player)
admin.site.register(Match)
admin.site.register(PlayerMatchStats)
