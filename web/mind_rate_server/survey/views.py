from django.core import serializers
from .models import Study, Questionnaire, TriggerEvent
from django.shortcuts import render, get_object_or_404, redirect, get_list_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType


# give user permissions and redirect user to the admin site
@login_required(login_url="login/")
def home(request):
    user = User.objects.get(username=request.user.username)

    # give user access to the admin site
    user.is_staff = True

    # give user all permissions of the survey app
    content_type_list = ContentType.objects.filter(app_label='survey')

    for content_type in content_type_list:
        user.user_permissions.add(
            *Permission.objects.filter(content_type=content_type)
        )

    user.save()

    # send user to the admin site
    return redirect('/admin/')


def view_answers(request, study_id):
    study = get_object_or_404(Study, pk=study_id)
    user = request.user
    return render(request, 'view_answers.html', {"study": study, "user": user})


# For app to download studies
# def view_download(request, study_id):
#     study = get_object_or_404(Study, pk=study_id)
#     study_in_json_str = serializers.serialize('json', [study, ])
#     questionnaire_list = get_list_or_404(Questionnaire, study_id=study.id)
#     questionnaire_in_json_str = ""
#     for questionnaire in questionnaire_list:
#         questionnaire_in_json_str += serializers.serialize('json', [questionnaire, ])
#     all_question_list = []
#     all_trigger_event_list = []
#     for questionnaire in questionnaire_list:
#         all_question_list.extend(get_list_or_404(Question, questionnaire_id=questionnaire.id))
#         all_trigger_event_list.extend(get_list_or_404(TriggerEvent, questionnaire_id=questionnaire.id))
#     all_question_in_json_str = ""
#     all_trigger_event_in_json_str = ""
#     for question in all_question_list:
#         all_question_in_json_str += serializers.serialize('json', [question, ])
#     for trigger_event in all_trigger_event_list:
#         all_trigger_event_in_json_str += serializers.serialize('json', [trigger_event, ])
#     return render(request, 'view_download.html',
#                   {"study": study_in_json_str, "questionnaires": questionnaire_in_json_str,
#                    "questions": all_question_in_json_str, "trigger_events": all_trigger_event_in_json_str})
#
#
# def preview(request, questionnaire_id):
#     questionnaire = get_object_or_404(Questionnaire, pk=questionnaire_id)
#     all_question_list = get_list_or_404(Question, questionnaire_id=questionnaire.id)
#     return render(request, 'preview.html', {"questionnaire": questionnaire, "question_list": all_question_list})
