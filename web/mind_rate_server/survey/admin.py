from django.contrib import admin

from .models import Questionnaire, Study, StudyDirector, TextQuestion, ChoiceQuestion, ScaleQuestion

admin.site.register(Questionnaire)
admin.site.register(Study)
admin.site.register(StudyDirector)
admin.site.register(ScaleQuestion)
admin.site.register(ChoiceQuestion)
admin.site.register(TextQuestion)
