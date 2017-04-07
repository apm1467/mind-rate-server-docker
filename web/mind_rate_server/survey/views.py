from .models import Questionnaire, Study, Proband, TextQuestion, SingleChoiceQuestion, MultiChoiceQuestion,\
    DragScaleQuestion, TriggerEvent, ChoiceOption, ProbandInfoQuestionnaire, ProbandInfoCell, QuestionnaireAnswer, \
    SensorValueCell, TextQuestionAnswer, SingleChoiceQuestionAnswer, MultiChoiceQuestionAnswer, DragScaleQuestionAnswer
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
import datetime


# give user permissions and redirect user to the admin site
@login_required(login_url="login/")
def home(request):
    user = User.objects.get(username=request.user.username)

    # give user access to the admin site
    user.is_staff = True

    # give user all permissions of the survey app
    content_type_list = ContentType.objects.filter(app_label='survey')
    for content_type in content_type_list:
        user.user_permissions.add(*Permission.objects.filter(content_type=content_type))

    user.save()

    # send user to the admin site
    return redirect('/admin/')


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
    if len(question_list) == 0:
        return "\"questions\": []"

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
            if isinstance(question, MultiChoiceQuestion):
                question_type = "MultipleChoice"
            else:
                question_type = "SingleChoice"
        else:  # the question is not a choice question
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
                     "\"questionContent\": \"%s\"," \
                     "\"showByDefault\": %s," \
                     % (question.id, question.question_text, show_by_default)

        # display question type specific data
        json_data += "\"questionType\": {" \
                     "\"typeName\": \"%s\"" % question_type

        # display options for choice question
        if question_type == "MultipleChoice" or question_type == "SingleChoice":
            json_data += ", \"options\": ["
            for option in option_list:

                # get next question id from next question position
                next_question_id = ""
                for q in question_list:
                    if q.position == option.next_question_position:
                        next_question_id = q.id
                        break

                json_data += "{\"optionContent\": \"%s\", \"nextQuestionID\": \"%s\"}," \
                             % (option.choice_text, next_question_id)

            json_data = json_data[:-1]  # remove the trailing comma
            json_data += "]"  # end of all options

        # display drag interval for drag scale question
        elif question_type == "DragScale":
            json_data += ", \"maxValue\""": %d" % question.max_value

        json_data += "}"  # end of question type
        json_data += "},"  # end of a question

    json_data = json_data[:-1]  # remove the trailing comma
    json_data += "]"   # end of all questions
    return json_data


# the 3 standard proband info questions showed during proband registration
def download_proband_info_questionnaire(request, study_id):
    study = get_object_or_404(Study, id=study_id)
    proband_info_questionnaire = ProbandInfoQuestionnaire.objects.get(study=study)

    if proband_info_questionnaire.ask_for_birthday:
        birthday = "true"
    else:
        birthday = "false"

    if proband_info_questionnaire.ask_for_gender:
        gender = "true"
    else:
        gender = "false"

    if proband_info_questionnaire.ask_for_occupation:
        occupation = "true"
    else:
        occupation = "false"

    json_data = "{" \
                "\"birthday\": %s," \
                "\"gender\": %s," \
                "\"occupation\": %s" \
                "}" % (birthday, gender, occupation)
    return HttpResponse(json_data, content_type="application/json")


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
                "\"second\": %d" \
                "}," \
                "\"endDate\": {" \
                "\"year\": %d," \
                "\"month\": %d," \
                "\"day\": %d," \
                "\"hour\": %d," \
                "\"minute\": %d," \
                "\"second\": %d" \
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
                     "\"second\": %d" \
                     "}," \
                     % (questionnaire.id, questionnaire.name, questionnaire.max_trigger_times_per_day, duration)

        if trigger_event.datetime is None:
            date_time = "null"
        else:
            date_time = "{" \
                       "\"year\": %d," \
                       "\"month\": %d," \
                       "\"day\": %d," \
                       "\"hour\": %d," \
                       "\"minute\": %d," \
                       "\"second\": %d" \
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
                     "\"time\": %s," % (trigger_event.min_time_space.total_seconds(), date_time, time)

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
            if trigger_event.relative_humidity == "VL":
                min_humidity = 0
                max_humidity = 20
            elif trigger_event.relative_humidity == "L":
                min_humidity = 0
                max_humidity = 40
            elif trigger_event.relative_humidity == "M":
                min_humidity = 30
                max_humidity = 70
            elif trigger_event.relative_humidity == "H":
                min_humidity = 60
                max_humidity = 100
            elif trigger_event.relative_humidity == "VH":
                min_humidity = 80
                max_humidity = 100
            else:
                min_humidity = 0
                max_humidity = 100
            json_data += "\"relativeHumidity\": true," \
                         "\"relativeHumidityMinValue\": %d," \
                         "\"relativeHumidityMaxValue\": %d," % (min_humidity, max_humidity)
        else:
            json_data += "\"relativeHumidity\": false,"

        if trigger_event.temperature is not None:
            if trigger_event.temperature == "VL":
                min_temperature = -50
                max_temperature = -10
            elif trigger_event.temperature == "L":
                min_temperature = -50
                max_temperature = 10
            elif trigger_event.temperature == "M":
                min_temperature = 10
                max_temperature = 25
            elif trigger_event.temperature == "H":
                min_temperature = 25
                max_temperature = 50
            elif trigger_event.temperature == "VH":
                min_temperature = 35
                max_temperature = 50
            else:
                min_temperature = -50
                max_temperature = 50
            json_data += "\"ambientTemperature\": true," \
                         "\"ambientTemperatureMinValue\": %d," \
                         "\"ambientTemperatureMaxValue\": %d," % (min_temperature, max_temperature)
        else:
            json_data += "\"ambientTemperature\": false,"

        if trigger_event.air_pressure is not None:
            if trigger_event.air_pressure == "VL":
                min_air_pressure = 300
                max_air_pressure = 600
            elif trigger_event.air_pressure == "L":
                min_air_pressure = 300
                max_air_pressure = 900
            elif trigger_event.air_pressure == "M":
                min_air_pressure = 900
                max_air_pressure = 1100
            elif trigger_event.air_pressure == "H":
                min_air_pressure = 1100
                max_air_pressure = 1300
            elif trigger_event.air_pressure == "VH":
                min_air_pressure = 1200
                max_air_pressure = 1300
            else:
                min_air_pressure = 300
                max_air_pressure = 1100
            json_data += "\"pressure\": true," \
                         "\"pressureMinValue\": %d," \
                         "\"pressureMaxValue\": %d," % (min_air_pressure, max_air_pressure)
        else:
            json_data += "\"pressure\": false,"

        if trigger_event.proximity is not None:
            if trigger_event.proximity == "VL":
                min_proximity = 0
                max_proximity = 1
            elif trigger_event.proximity == "L":
                min_proximity = 0
                max_proximity = 3
            elif trigger_event.proximity == "M":
                min_proximity = 3
                max_proximity = 6
            elif trigger_event.proximity == "H":
                min_proximity = 6
                max_proximity = 10
            elif trigger_event.proximity == "VH":
                min_proximity = 8
                max_proximity = 10
            else:
                min_proximity = 0
                max_proximity = 10
            json_data += "\"proximity\": true," \
                         "\"proximityMinValue\": %d," \
                         "\"proximityMaxValue\": %d" % (min_proximity, max_proximity)
        else:
            json_data += "\"proximity\": false"
        json_data += "},"

        # questions of the questionnaire
        json_data += _get_question_list_json(
            _get_question_list_from_questionnaire(questionnaire)
        )

        json_data += "},"  # end of a questionnaire

    json_data = json_data[:-1]  # remove the trailing comma
    json_data += "]"  # end of all questionnaires
    json_data += "}"  # end of study
    json_data += "}"  # end of json

    return HttpResponse(json_data, content_type="application/json")


@csrf_exempt
def receive_answer(request):
    # write received request to log
    now = datetime.datetime.now().strftime('%m %d %H:%M:%S')
    log = open('/usr/src/app/log.txt', 'a')
    log.write('\n\n%s\n%s' % (now, request.body))

    json_data = json.loads(request.body.replace('\\n', ''))
    proband = get_object_or_404(Proband, id=json_data['probandID'])

    if 'questionnaireID' not in json_data:  # the 3 standard proband info questions
        # store proband info
        if 'birthday' in json_data:
            ProbandInfoCell.objects.create(proband=proband, key='birthday', value=json_data['birthday'])
        if 'gender' in json_data:
            ProbandInfoCell.objects.create(proband=proband, key='gender', value=json_data['gender'])
        if 'occupation' in json_data:
            ProbandInfoCell.objects.create(proband=proband, key='occupation', value=json_data['occupation'])

    elif json_data['questionnaireID'] == 'probandInfoQuestionnaire':  # custom proband info questions
        for question_item in json_data['questionAnswer']:

            # get the question object
            question_type = question_item['questionType']
            if question_type == 'SingleChoice':
                question = get_object_or_404(SingleChoiceQuestion, id=question_item['questionID'])
            elif question_type == 'TextAnswer':
                question = get_object_or_404(TextQuestion, id=question_item['questionID'])
            elif question_type == 'DragScale':
                question = get_object_or_404(DragScaleQuestion, id=question_item['questionID'])
            elif question_type == 'MultipleChoice':
                question = get_object_or_404(MultiChoiceQuestion, id=question_item['questionID'])

            # store proband info
            ProbandInfoCell.objects.create(proband=proband, key=question.question_text, value=question_item['answer'])

    else:  # normal questionnaire
        questionnaire = get_object_or_404(Questionnaire, id=json_data['questionnaireID'])
        submit_time_dict = json_data['submitTime']
        submit_time = datetime.datetime(submit_time_dict['year'], submit_time_dict['month'],
                                        submit_time_dict['day'], submit_time_dict['hour'],
                                        submit_time_dict['minute'], submit_time_dict['second'])

        # create questionnaire answer object
        questionnaire_answer = QuestionnaireAnswer.objects.create(questionnaire=questionnaire, submitter=proband,
                                                                  submit_time=submit_time)

        # store sensor values of the questionnaire answer
        for key, value in json_data['sensorValues']:
            SensorValueCell.objects.create(questionnaire_answer=questionnaire_answer, key=key, value=value)

        # store answers of each question
        for question_item in json_data['questionAnswer']:
            question_type = question_item['questionType']
            if question_type == 'SingleChoice':
                question = get_object_or_404(SingleChoiceQuestion, id=question_item['questionID'])
                SingleChoiceQuestionAnswer.objects.create(question=question, value=question_item['answer'],
                                                          questionnaire_answer=questionnaire_answer)
            elif question_type == 'TextAnswer':
                question = get_object_or_404(TextQuestion, id=question_item['questionID'])
                TextQuestionAnswer.objects.create(question=question, value=question_item['answer'],
                                                  questionnaire_answer=questionnaire_answer)
            elif question_type == 'DragScale':
                question = get_object_or_404(DragScaleQuestion, id=question_item['questionID'])
                DragScaleQuestionAnswer.objects.create(question=question, value=question_item['answer'],
                                                       questionnaire_answer=questionnaire_answer)
            elif question_type == 'MultipleChoice':
                question = get_object_or_404(MultiChoiceQuestion, id=question_item['questionID'])
                MultiChoiceQuestionAnswer.objects.create(question=question, value=question_item['answer'],
                                                         questionnaire_answer=questionnaire_answer)

    proband.study.answer_updated_times += 1  # update received answers counter
    return HttpResponse("OK", content_type="text/plain")


def view_log(request):
    log = open('/usr/src/app/log.txt', 'r')
    return HttpResponse(log.read(), content_type="text/plain")


def preview(request, questionnaire_id):
    questionnaire = get_object_or_404(Questionnaire, pk=questionnaire_id)
    all_question_list = _get_question_list_from_questionnaire(questionnaire)
    return render(request, 'preview.html', {"questionnaire": questionnaire, "question_list": all_question_list})
