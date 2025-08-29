from django.shortcuts import render, redirect
from django.views import View
from training_app.models import TrainingSession
from players_app.models import Player
from training_app.utils.create_session_util import create_training_session  # <-- import utility


class TrainingSessionCreateView(View):
    def get(self, request):
        training_choices = TrainingSession.TRAINING_TYPE_CHOICES
        players = Player.objects.all()
        return render(request, 'training_app/create_session.html', {
            'training_choices': training_choices,
            'players': players,
        })

    def post(self, request):
        duration = request.POST.get('duration')
        training_types = request.POST.getlist('training_types')
        player_ids = request.POST.getlist('players')

        create_training_session(duration, training_types, player_ids)

        return redirect('training_session_list')


class TrainingSessionListView(View):
    def get(self, request):
        sessions = TrainingSession.objects.all().order_by('-date')
        return render(request, 'training_app/session_list.html', {'sessions': sessions})
