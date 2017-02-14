from django.contrib import admin

from .models import Questionnaire, Study, StudyDirector, TextQuestion, \
ChoiceQuestion, ScaleQuestion, TriggerEvent

class QuestionnaireInline(admin.TabularInline):
    model = Questionnaire
    extra = 1

class StudyAdmin(admin.ModelAdmin):
    list_display = ('study_name', 'start_date_time', 'end_date_time')
    inlines = [QuestionnaireInline]

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

class QuestionnaireAdmin(admin.ModelAdmin):
    inlines = [TextQuestionInline, ChoiceQuestionInline, ScaleQuestionInline,
    TriggerEventInline]
    list_display = ('questionnaire_name', 'required_submit_date_time')

admin.site.register(Study, StudyAdmin)
admin.site.register(Questionnaire, QuestionnaireAdmin)
admin.site.register(StudyDirector)
admin.site.register(ChoiceQuestion)
