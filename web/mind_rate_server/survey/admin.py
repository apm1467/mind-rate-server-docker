from django.contrib import admin
from .models import Questionnaire, Study, TextQuestion, \
    ChoiceQuestion, ScaleQuestion, TriggerEvent
from django.contrib.auth.models import User, Permission


class TextQuestionInline(admin.TabularInline):
    model = TextQuestion
    extra = 1

class ChoiceQuestionInline(admin.TabularInline):
    model = ChoiceQuestion
    extra = 1

class ScaleQuestionInline(admin.TabularInline):
    model = ScaleQuestion
    extra = 1

class TriggerEventInline(admin.TabularInline):
    model = TriggerEvent
    extra = 1


class QuestionnaireInline(admin.StackedInline):
    model = Questionnaire
    inlines = [TextQuestionInline, ChoiceQuestionInline, ScaleQuestionInline,
               TriggerEventInline]
    fields = ['name', 'due_after', 'max_trigger_times_per_day']
    list_display = ('name', 'due_after', 'max_trigger_times_per_day')
    extra = 0


class StudyAdmin(admin.ModelAdmin):
    model = Study
    fields = ['name', 'start_date_time', 'end_date_time']  # which fields will be asked
    list_display = ('name', 'start_date_time', 'end_date_time') # fields displayed on the change list page
    inlines = [QuestionnaireInline]

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

    # override to set object level change permission
    def has_delete_permission(self, request, obj=None):
        if obj is None:
            return True
        return obj.owner == request.user

    # override to always allow access to the module's index page
    def has_module_permission(self, request):
        return True


admin.site.register(Study, StudyAdmin)
