from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render


@staff_member_required
def home_view(request):
    return render(request, "psychology_app_v2/home.html")
