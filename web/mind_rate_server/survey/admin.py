from django.contrib import admin
import nested_admin
from .models import Questionnaire, Study, TextQuestion, SingleChoiceQuestion, MultiChoiceQuestion,\
    DragScaleQuestion, TriggerEvent, ChoiceOption, ProbandInfoQuestionnaire, QuestionnaireAnswer,\
    TextQuestionAnswer, SingleChoiceQuestionAnswer, MultiChoiceQuestionAnswer, DragScaleQuestionAnswer
from django.contrib.auth.models import User
from django.http import HttpResponse
import csv


class TextQuestionInline(nested_admin.NestedStackedInline):
    model = TextQuestion
    fields = ['show_by_default', 'question_text', 'position']
    sortable_field_name = 'position'
    extra = 0


class ChoiceOptionInline(nested_admin.NestedStackedInline):
    model = ChoiceOption
    fieldsets = [
        (None, {'fields': ['choice_text']}),

        ('(Optional) follow up question for this choice option', {'fields': ['next_question_position']})
    ]
    extra = 0


class SingleChoiceQuestionInline(nested_admin.NestedStackedInline):
    model = SingleChoiceQuestion
    fields = ['show_by_default', 'question_text', 'position']
    inlines = [ChoiceOptionInline]
    sortable_field_name = 'position'
    sortable_excludes = ('show_by_default', 'question_text', 'position')
    extra = 0


class MultiChoiceQuestionInline(nested_admin.NestedStackedInline):
    model = MultiChoiceQuestion
    fields = ['show_by_default', 'question_text', 'position']
    inlines = [ChoiceOptionInline]
    sortable_field_name = 'position'
    sortable_excludes = ('show_by_default', 'question_text', 'position')
    extra = 0


class DragScaleQuestionInline(nested_admin.NestedStackedInline):
    model = DragScaleQuestion
    fields = ['show_by_default', 'question_text', 'min_value', 'max_value', 'position']
    sortable_field_name = 'position'
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
    min_num = 1
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
    inlines = [TextQuestionInline, SingleChoiceQuestionInline, MultiChoiceQuestionInline, DragScaleQuestionInline]
    extra = 0
    max_num = 1


def export_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="study_data.csv"'

    writer = csv.writer(response)
    writer.writerow(['Study ID', 'Questionnaire ID', 'Question ID', 'Answer', 'Submit Time'])

    for study in queryset:
        questionnaire_list = Questionnaire.objects.filter(study=study)

        for questionnaire in questionnaire_list:
            questionnaire_answer_list = QuestionnaireAnswer.objects.filter(questionnaire=questionnaire)

            for questionnaire_answer in questionnaire_answer_list:
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

                for question_answer in question_answer_list:
                    writer.writerow([
                        study.id, questionnaire.id, question_answer.question.id,
                        question_answer.value, question_answer.questionnaire_answer.submit_time
                    ])

    return response


class StudyAdmin(nested_admin.NestedModelAdmin):
    model = Study
    fields = ['name', 'start_date_time', 'end_date_time']  # which fields will be asked
    list_display = ('name', 'start_date_time', 'end_date_time')  # fields displayed on the change list page
    inlines = [ProbandInfoQuestionnaireInline, QuestionnaireInline]
    actions = [export_csv]

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
