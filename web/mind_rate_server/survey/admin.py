from django.contrib import admin

from .models import Questionnaire, Study, StudyDirector, CommonQuestion

class QuestionAdmin(admin.ModelAdmin):
    pass

admin.site.register(CommonQuestion)
admin.site.register(Questionnaire)
admin.site.register(Study)
admin.site.register(StudyDirector)
