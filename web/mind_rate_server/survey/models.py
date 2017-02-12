from django.db import models

class Questionnaire(models.Model):
    name = models.CharField(max_length=200)


class Question(models.Model):
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.CASCADE)
    question_text = models.CharField(max_length=200)
