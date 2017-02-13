from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views import generic

from .models import Study


@login_required(login_url="login/")
def home(request):
    return render(request,"home.html")

def view_answers(request, study_id):
    study = get_object_or_404(Study, pk = study_id)
    return render(request, 'view_answers.html', {"study":study})
