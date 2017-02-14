from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views import generic
from django.contrib.auth.models import User

from .models import Study


@login_required(login_url="login/")
def home(request):

    # give user permission to access the admin site
    user = User.objects.get(username=request.user.username)
    user.is_staff = True
    user.save()

    # send user to admin site
    return redirect('/admin/')


def view_answers(request, study_id):
    study = get_object_or_404(Study, pk = study_id)
    return render(request, 'view_answers.html', {"study":study})

def preview(request, questionnaire_id):
    questionnaire = get_object_or_404(Study, pk = questionnaire_id)
    return render(request, 'preview.html', {"questionnaire":questionnaire})
