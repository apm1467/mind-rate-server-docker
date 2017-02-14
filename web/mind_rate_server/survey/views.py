from django.shortcuts import render, get_object_or_404, redirect, get_list_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views import generic
from django.contrib.auth.models import User

from .models import Study, TextQuestion, ChoiceQuestion, ScaleQuestion, Questionnaire


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
    user = request.user
    return render(request, 'view_answers.html', {"study":study, "user":user})

def preview(request, questionnaire_id):
    questionnaire = get_object_or_404(Questionnaire, pk = questionnaire_id)
    text_question_list = list(TextQuestion.objects.filter(questionnaire_id=questionnaire_id))
    choice_question_list = list(ChoiceQuestion.objects.filter(questionnaire_id=questionnaire_id))
    scale_question_list = list(ScaleQuestion.objects.filter(questionnaire_id=questionnaire_id))
    question_list = text_question_list + choice_question_list + scale_question_list

    return render(request, 'preview.html', {"questionnaire":questionnaire,
    "question_list":question_list, "text_question_list":text_question_list,
    "choice_question_list":choice_question_list, "scale_question_list":scale_question_list})
