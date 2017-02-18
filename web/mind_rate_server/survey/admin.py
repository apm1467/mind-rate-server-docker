from django.contrib import admin
import nested_admin
from .models import Questionnaire, Study, TextQuestion, SingleChoiceQuestion, MultiChoiceQuestion,\
    DragScaleQuestion, TriggerEvent, ChoiceOption, ProbandInfoQuestionnaire
from django.contrib.auth.models import User


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
    classes = ('grp-collapse grp-open',)
    sortable_field_name = 'position'
    extra = 0


class MultiChoiceQuestionInline(nested_admin.NestedStackedInline):
    model = MultiChoiceQuestion
    fields = ['show_by_default', 'question_text', 'position']
    inlines = [ChoiceOptionInline]
    sortable_field_name = 'position'
    extra = 0


class DragScaleQuestionInline(nested_admin.NestedStackedInline):
    model = DragScaleQuestion
    fields = ['show_by_default', 'question_text', 'min_value', 'max_value', 'position']
    sortable_field_name = 'position'
    extra = 0


class TriggerEventInline(nested_admin.NestedStackedInline):
    model = TriggerEvent
    fieldsets = [
        (None, {'fields': ['min_time_space']}),

        ('trigger options based on time', {'fields': ['datetime', 'time']}),

        ('trigger options based on calender, calls or notifications',
         {'fields': ['triggeredWhenCalendarEventBegins', 'triggeredWhenCalendarEventEnds',
                     'triggeredWhenFacebookNotificationComes', 'triggeredWhenWhatsAppNotificationComes',
                     'triggeredWhenSmsComes', 'triggeredWhenPhoneCallEnds']}),

        ('trigger options based on user activities', {'fields': ['user_activity']}),

        ('trigger options based on environment sensors',
         {'fields': ['light', 'relative_humidity', 'air_pressure', 'proximity']})
    ]
    list_display = ('name', 'due_after', 'max_trigger_times_per_day')
    extra = 0


class QuestionnaireInline(nested_admin.NestedStackedInline):
    model = Questionnaire
    inlines = [TriggerEventInline, TextQuestionInline, SingleChoiceQuestionInline,
               MultiChoiceQuestionInline, DragScaleQuestionInline]
    fields = ['name', 'due_after', 'max_trigger_times_per_day']
    list_display = ('name', 'due_after', 'max_trigger_times_per_day')
    extra = 0


class ProbandInfoQuestionnaireInline(nested_admin.NestedStackedInline):
    model = ProbandInfoQuestionnaire
    inlines = [TextQuestionInline, SingleChoiceQuestionInline, MultiChoiceQuestionInline, DragScaleQuestionInline]
    extra = 0


class StudyAdmin(nested_admin.NestedModelAdmin):
    model = Study
    fields = ['name', 'start_date_time', 'end_date_time']  # which fields will be asked
    list_display = ('name', 'start_date_time', 'end_date_time')  # fields displayed on the change list page
    inlines = [ProbandInfoQuestionnaireInline, QuestionnaireInline]

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

    # override to set object level change permission
    def has_change_permission(self, request, obj=None):
        if obj is None:
            return True
        return obj.owner == request.user

    # override to set object level delete permission
    def has_delete_permission(self, request, obj=None):
        if obj is None:
            return True
        return obj.owner == request.user

    # override to always allow access to the module's index page
    def has_module_permission(self, request):
        return True


admin.site.register(Study, StudyAdmin)
