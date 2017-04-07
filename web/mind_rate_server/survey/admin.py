from django.contrib import admin
import nested_admin
from .models import Questionnaire, Study, TextQuestion, SingleChoiceQuestion, MultiChoiceQuestion,\
    DragScaleQuestion, TriggerEvent, ChoiceOption, ProbandInfoQuestionnaire, QuestionnaireAnswer,\
    TextQuestionAnswer, SingleChoiceQuestionAnswer, MultiChoiceQuestionAnswer, DragScaleQuestionAnswer,\
    SensorValueCell, Proband, ProbandInfoCell
from .views import _get_question_list_from_questionnaire
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render
import csv


class TextQuestionInline(nested_admin.NestedStackedInline):
    model = TextQuestion
    fields = ['show_by_default', 'question_text', 'position']
    # sortable_field_name = 'position'
    extra = 0


class ChoiceOptionInline(nested_admin.NestedTabularInline):
    model = ChoiceOption
    fieldsets = [
        (None, {'fields': ['choice_text']}),

        ('(Optional) follow up question for this choice option', {'fields': ['next_question_position']})
    ]
    min_num = 2
    extra = 0


class SingleChoiceQuestionInline(nested_admin.NestedStackedInline):
    model = SingleChoiceQuestion
    fields = ['show_by_default', 'question_text', 'position']
    inlines = [ChoiceOptionInline]
    # sortable_field_name = 'position'
    sortable_excludes = ('show_by_default', 'question_text', 'position')
    extra = 0


class MultiChoiceQuestionInline(nested_admin.NestedStackedInline):
    model = MultiChoiceQuestion
    fields = ['show_by_default', 'question_text', 'position']
    inlines = [ChoiceOptionInline]
    # sortable_field_name = 'position'
    sortable_excludes = ('show_by_default', 'question_text', 'position')
    extra = 0


class DragScaleQuestionInline(nested_admin.NestedStackedInline):
    model = DragScaleQuestion
    fields = ['show_by_default', 'question_text', 'min_value', 'max_value', 'position']
    # sortable_field_name = 'position'
    sortable_excludes = ('show_by_default', 'question_text', 'min_value', 'max_value', 'position')
    extra = 0


class TriggerEventInline(nested_admin.NestedStackedInline):
    model = TriggerEvent
    fieldsets = [
        (None, {'fields': ['min_time_space']}),

        ('trigger options based on time', {'fields': ['datetime', 'time']}),

        ('trigger options based on calender, SMS, calls or notifications',
         {'fields': ['triggeredWhenCalendarEventBegins', 'triggeredWhenCalendarEventEnds',
                     'triggeredWhenFacebookNotificationComes', 'triggeredWhenWhatsAppNotificationComes',
                     'triggeredWhenSmsComes', 'triggeredWhenPhoneCallEnds']}),

        ('trigger options based on user activities', {'fields': ['user_activity']}),

        ('trigger options based on environment sensors',
         {'fields': ['light', 'temperature', 'relative_humidity', 'air_pressure', 'proximity']})
    ]
    list_display = ('name', 'due_after', 'max_trigger_times_per_day')
    extra = 0
    min_num = 0
    max_num = 1


class QuestionnaireInline(nested_admin.NestedStackedInline):
    model = Questionnaire
    inlines = [TriggerEventInline, TextQuestionInline, SingleChoiceQuestionInline,
               MultiChoiceQuestionInline, DragScaleQuestionInline]
    fields = ['name', 'due_after', 'max_trigger_times_per_day']
    list_display = ('name', 'due_after', 'max_trigger_times_per_day')
    extra = 0
    min_num = 1


class ProbandInfoQuestionnaireInline(nested_admin.NestedStackedInline):
    model = ProbandInfoQuestionnaire
    fields = ['ask_for_birthday', 'ask_for_occupation', 'ask_for_gender']
    inlines = [TextQuestionInline, SingleChoiceQuestionInline, MultiChoiceQuestionInline, DragScaleQuestionInline]
    extra = 0
    max_num = 1


def export_proband_info(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="proband_info.csv"'

    for study in queryset:
        proband_list = Proband.objects.filter(study=study)

        # get all proband info cell keys
        proband_info_keys = set()
        for proband in proband_list:
            proband_info_cell_list = ProbandInfoCell.objects.filter(proband=proband)
            for proband_info_cell in proband_info_cell_list:
                proband_info_keys.add(proband_info_cell.key)
        proband_info_keys = list(proband_info_keys)  # convert to list because set is unordered

        # write title line
        writer = csv.writer(response)
        writer.writerow(['Study ID', 'Proband ID'] + proband_info_keys)

        for proband in proband_list:
            proband_info_cell_list = ProbandInfoCell.objects.filter(proband=proband)
            # skip all probands without valid proband info
            if not proband_info_cell_list:
                continue

            info_list = []
            for key in proband_info_keys:
                if not ProbandInfoCell.objects.filter(proband=proband, key=key):
                    info_list.append(' ')
                else:
                    info_list.append(ProbandInfoCell.objects.filter(proband=proband, key=key).last().value)

            # write info line for each proband
            writer.writerow([study.id, proband.id] + info_list)

        writer.writerow([''])  # an empty line for each study

    return response


def export_study_answer(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="study_answer.csv"'

    writer = csv.writer(response)
    writer.writerow(['Study ID', 'Questionnaire ID', 'Question', 'Answer', 'Proband ID', 'Submit Time', 'Sensor value'])

    for study in queryset:
        questionnaire_list = Questionnaire.objects.filter(study=study)

        for questionnaire in questionnaire_list:
            questionnaire_answer_list = QuestionnaireAnswer.objects.filter(questionnaire=questionnaire)

            for questionnaire_answer in questionnaire_answer_list:

                # write all sensor values into a string
                sensor_value = ""
                sensor_value_cell_list = SensorValueCell.objects.filter(questionnaire_answer=questionnaire_answer)
                for sensor_value_cell in sensor_value_cell_list:
                    sensor_value += "%s: %s / " % (sensor_value_cell.key, sensor_value_cell.value)
                    sensor_value = sensor_value[:-3]  # remove the trailing slash

                # make a list of all question answers
                question_answer_list = []
                question_answer_list.extend(TextQuestionAnswer.objects.filter(
                    questionnaire_answer=questionnaire_answer))
                question_answer_list.extend(SingleChoiceQuestionAnswer.objects.filter(
                    questionnaire_answer=questionnaire_answer))
                question_answer_list.extend(MultiChoiceQuestionAnswer.objects.filter(
                    questionnaire_answer=questionnaire_answer))
                question_answer_list.extend(DragScaleQuestionAnswer.objects.filter(
                    questionnaire_answer=questionnaire_answer))

                # sort the question answer list based on submit time
                question_answer_list.sort(key=lambda item: item.questionnaire_answer.submit_time)

                # write all values into a csv row
                for question_answer in question_answer_list:
                    writer.writerow([
                        study.id, questionnaire.id, question_answer.question.question_text,
                        question_answer.value, question_answer.questionnaire_answer.submitter.id,
                        question_answer.questionnaire_answer.submit_time, sensor_value
                    ])

        writer.writerow([''])  # an empty line for each study

    return response


def preview_questions(modeladmin, request, queryset):
    study_list = []
    for study in queryset:
        study_dict = {"name": study.name, "questionnaires": []}
        study_list.append(study_dict)

        questionnaire_list = Questionnaire.objects.filter(study=study)
        for questionnaire in questionnaire_list:
            questionnaire_dict = {"id": questionnaire.id, "questions": []}
            study_list[-1]["questionnaires"].append(questionnaire_dict)

            question_list = _get_question_list_from_questionnaire(questionnaire)
            for question in question_list:
                question_options = ""

                if isinstance(question, SingleChoiceQuestion):
                    question_options += "<ol>"
                    option_list = ChoiceOption.objects.filter(single_choice_question=question)
                    for option in option_list:
                        if option.next_question_position is None:
                            question_options += "<li>" + option.choice_text + "</li>"
                        else:
                            question_options += "<li>" + option.choice_text + " → <b>Question " + \
                                                str(option.next_question_position) + "</b></li>"
                    question_options += "</ol>"

                elif isinstance(question, MultiChoiceQuestion):
                    question_options += "<ol>"
                    option_list = ChoiceOption.objects.filter(multi_choice_question=question)
                    for option in option_list:
                        question_options += "<li>" + option.choice_text + "</li>"
                    question_options += "</ol>"

                elif isinstance(question, DragScaleQuestion):
                    question_options = "Range: %d – %d" % (question.min_value, question.max_value)

                elif isinstance(question, TextQuestion):
                    question_options = "Text question"

                if question.show_by_default:
                    visibility = "Show by default"
                else:
                    visibility = "Not show by default"

                question_dict = {"position": question.position, "text": question.question_text,
                                 "options": question_options, "visibility": visibility}
                study_list[-1]["questionnaires"][-1]["questions"].append(question_dict)

    return render(request, 'preview.html', {"study_list": study_list})


class StudyAdmin(nested_admin.NestedModelAdmin):
    model = Study
    fields = ['name', 'start_date_time', 'end_date_time']
    list_display = ('name', 'id', 'start_date_time', 'end_date_time', 'answer_updated_times')
    inlines = [ProbandInfoQuestionnaireInline, QuestionnaireInline]
    actions = [preview_questions, export_proband_info, export_study_answer]

    # override to attach request.user to the object prior to saving
    def save_model(self, request, obj, form, change):
        user = User.objects.get(username=request.user.username)
        obj.owner = user
        super(StudyAdmin, self).save_model(request, obj, form, change)

    # override to show objects owned by the logged-in user
    def get_queryset(self, request):
        qs = super(StudyAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(owner=request.user)


admin.site.register(Study, StudyAdmin)
