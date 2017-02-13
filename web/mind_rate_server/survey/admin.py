from django.contrib import admin

from .models import Questionnaire, Study, StudyDirector

admin.site.register(Questionnaire)
admin.site.register(Study)
admin.site.register(StudyDirector)
