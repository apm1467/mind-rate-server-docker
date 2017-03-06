from .models import Questionnaire, Study, Proband, TextQuestion, SingleChoiceQuestion, MultiChoiceQuestion,\
    DragScaleQuestion, TriggerEvent, ChoiceOption, ProbandInfoQuestionnaire
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse


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


def _get_question_list_from_questionnaire(questionnaire):
    question_list = []

    question_list.extend(TextQuestion.objects.filter(questionnaire=questionnaire))
    question_list.extend(DragScaleQuestion.objects.filter(questionnaire=questionnaire))
    question_list.extend(SingleChoiceQuestion.objects.filter(questionnaire=questionnaire))
    question_list.extend(MultiChoiceQuestion.objects.filter(questionnaire=questionnaire))

    question_list.sort(key=lambda question: question.position)
    return question_list


def _get_question_list_from_proband_info_questionnaire(proband_info_questionnaire):
    question_list = []

    question_list.extend(TextQuestion.objects.filter(proband_info_questionnaire=proband_info_questionnaire))
    question_list.extend(DragScaleQuestion.objects.filter(proband_info_questionnaire=proband_info_questionnaire))
    question_list.extend(SingleChoiceQuestion.objects.filter(proband_info_questionnaire=proband_info_questionnaire))
    question_list.extend(MultiChoiceQuestion.objects.filter(proband_info_questionnaire=proband_info_questionnaire))

    question_list.sort(key=lambda question: question.position)
    return question_list


def _get_question_list_json(question_list):
    json_data = "\"questions\": ["

    for question in question_list:
        option_list = []

        if isinstance(question, SingleChoiceQuestion):
            option_list.extend(ChoiceOption.objects.filter(single_choice_question=question))
        if isinstance(question, MultiChoiceQuestion):
            option_list.extend(ChoiceOption.objects.filter(multi_choice_question=question))
        if isinstance(question, TextQuestion):
            option_list.extend(ChoiceOption.objects.filter(text_question=question))
        if isinstance(question, DragScaleQuestion):
            option_list.extend(ChoiceOption.objects.filter(drag_scale_question=question))

        if len(option_list) != 0:  # the question must be a choice question
            has_choice = True
            if isinstance(question, MultiChoiceQuestion):
                question_type = "MultipleChoice"
            else:
                question_type = "SingleChoice"
        else:  # the question is no a choice question
            has_choice = False
            if isinstance(question, TextQuestion):
                question_type = "TextAnswer"
            else:
                question_type = "DragScale"

        if question.show_by_default:
            show_by_default = "true"
        else:
            show_by_default = "false"

        json_data += "{" \
                     "\"questionID\": \"%d\"," \
                     "\"questionType\": \"%s\"," \
                     "\"questionContent\": \"%s\"," \
                     "\"showByDefault\": %s," \
                     % (question.id, question_type, question.question_text, show_by_default)

        # display all options for choice question
        if has_choice:
            json_data += "\"options\": ["
            for option in option_list:

                # get next question id from next question position
                next_question_id = ""
                for q in question_list:
                    if q.position == option.next_question_position:
                        next_question_id = q.id
                        break

                json_data += "{\"optionContent\": \"%s\", \"nextQuestionID\": \"%s\"}," \
                             % (option.choice_text, next_question_id)

            json_data += "]"  # end of all choices

        # display drag interval for drag scale question
        elif isinstance(question, DragScaleQuestion):
            json_data += "\"maxValue\""": %d," % question.max_value

        json_data += "},"  # end of a question

    json_data += "],"   # end of all questions
    return json_data


# For app to download studies
def download(request, study_id):
    study = get_object_or_404(Study, id=study_id)
    proband = Proband.objects.create(study=study)
    proband_info_questionnaire = ProbandInfoQuestionnaire.objects.get(study=study)
    questionnaire_list = Questionnaire.objects.filter(study=study)

    start_time = study.start_date_time
    end_time = study.end_date_time

    # study basic info
    json_data = "{" \
                "\"study\": {" \
                "\"probandID\": \"%d\"," \
                "\"studyId\": \"%d\"," \
                "\"studyName\": \"%s\"," \
                "\"beginningDate\": {" \
                "\"year\": %d," \
                "\"month\": %d," \
                "\"day\": %d," \
                "\"hour\": %d," \
                "\"minute\": %d," \
                "\"second\": %d," \
                "}," \
                "\"endDate\": {" \
                "\"year\": %d," \
                "\"month\": %d," \
                "\"day\": %d," \
                "\"hour\": %d," \
                "\"minute\": %d," \
                "\"second\": %d," \
                "}," \
                % (proband.id, study.id, study.name, start_time.year, start_time.month, start_time.day,
                   start_time.hour, start_time.minute, start_time.second, study.end_date_time.year, end_time.month,
                   end_time.day, end_time.hour, end_time.minute, end_time.second)

    # proband info questionnaire
    json_data += "\"probandInfoQuestionnaire\": {"
    json_data += _get_question_list_json(
        _get_question_list_from_proband_info_questionnaire(proband_info_questionnaire)
    )
    json_data += "},"

    # normal questionnaires
    json_data += "\"questionnaires\": ["
    for questionnaire in questionnaire_list:
        trigger_event = TriggerEvent.objects.get(questionnaire=questionnaire)
        if questionnaire.due_after is None:
            duration = 999999999  # default unlimited duration time
        else:
            duration = questionnaire.due_after.total_seconds()

        # basic info of a questionnaire
        json_data += "{" \
                     "\"questionnaireID\": \"%d\"," \
                     "\"questionnaireName\": \"%s\"," \
                     "\"maxShowUpTimesPerDay\": %d," \
                     "\"duration\": {" \
                     "\"second\": %d," \
                     "}," \
                     % (questionnaire.id, questionnaire.name, questionnaire.max_trigger_times_per_day, duration)

        if trigger_event.datetime is None:
            datetime = "null"
        else:
            datetime = "{" \
                       "\"year\": %d," \
                       "\"month\": %d," \
                       "\"day\": %d," \
                       "\"hour\": %d," \
                       "\"minute\": %d," \
                       "\"second\": %d," \
                       "}" \
                       % (trigger_event.datetime.year, trigger_event.datetime.month, trigger_event.datetime.day,
                          trigger_event.datetime.hour, trigger_event.datetime.minute, trigger_event.datetime.second)
        if trigger_event.time is None:
            time = "null"
        else:
            time = "\"%d-%d-%d\"" % (trigger_event.time.hour, trigger_event.time.minute, trigger_event.time.second)

        # trigger event of questionnaire
        json_data += "\"triggerEvent\": {" \
                     "\"minTimeSpace\": %d," \
                     "\"datetime\": %s," \
                     "\"time\": %s," % (trigger_event.min_time_space.total_seconds(), datetime, time)

        if trigger_event.light is not None:
            if trigger_event.light == "VL":
                min_light = 0
                max_light = 4
            elif trigger_event.light == "L":
                min_light = 0
                max_light = 50
            elif trigger_event.light == "M":
                min_light = 50
                max_light = 400
            elif trigger_event.light == "H":
                min_light = 400
                max_light = 40000
            elif trigger_event.light == "VH":
                min_light = 1000
                max_light = 40000
            else:
                min_light = 0
                max_light = 40000
            json_data += "\"light\": true," \
                         "\"lightMinValue\": %d," \
                         "\"lightMaxValue\": %d," % (min_light, max_light)
        else:
            json_data += "\"light\": false,"

        if trigger_event.relative_humidity is not None:
            json_data += "\"relativeHumidity\": true," \
                         "\"relativeHumidityMinValue\": 0," \
                         "\"relativeHumidityMaxValue\": 0,"
        else:
            json_data += "\"relativeHumidity\": false,"

        if trigger_event.temperature is not None:
            json_data += "\"ambientTemperature\": true," \
                         "\"ambientTemperatureMinValue\": 0," \
                         "\"ambientTemperatureMaxValue\": 0,"
        else:
            json_data += "\"ambientTemperature\": false,"

        if trigger_event.air_pressure is not None:
            json_data += "\"pressure\": true," \
                         "\"pressureMinValue\": 0," \
                         "\"pressureMaxValue\": 0,"
        else:
            json_data += "\"pressure\": false,"

        if trigger_event.proximity is not None:
            json_data += "\"proximity\": true," \
                         "\"proximityMinValue\": 0," \
                         "\"proximityMaxValue\": 0,"
        else:
            json_data += "\"proximity\": false,"
        json_data += "},"

        # questions of the questionnaire
        json_data += _get_question_list_json(
            _get_question_list_from_questionnaire(questionnaire)
        )

        json_data += "},"  # end of a questionnaire

    json_data += "]"  # end of all questionnaires
    json_data += "}"  # end of study
    json_data += "}"  # end of json

    return HttpResponse(json_data, content_type="application/json")


def preview(request, questionnaire_id):
    questionnaire = get_object_or_404(Questionnaire, pk=questionnaire_id)
    all_question_list = _get_question_list_from_questionnaire(questionnaire)
    return render(request, 'preview.html', {"questionnaire": questionnaire, "question_list": all_question_list})
