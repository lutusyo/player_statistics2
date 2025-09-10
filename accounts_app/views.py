from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from teams_app.models import Team


def index(request):
    team = Team.objects.filter(age_group__code='U20', team_type='OUR_TEAM').first()

    return render(request, 'accounts_app/index.html', {'team': team})


def home_view(request):
    return render(request, 'base.html')


def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')  # Replace 'home' with your actual homepage view name
    else:
        form = UserCreationForm()
    return render(request, 'accounts_app/signup.html', {'form': form})
