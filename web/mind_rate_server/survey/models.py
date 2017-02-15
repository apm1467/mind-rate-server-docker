from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User

'''
CAUTION: when initializing an instance of this class, be sure to catch the IntegrityError, which is caused by a duplicate of primary key "mail_address" in table StudyDirector
'''
class StudyDirector(models.Model):
    '''
    To check whether the mail address is validated
    An unvalid mail address will cause ValidationError
    '''
    mail_address = models.EmailField("Email-Address", max_length=50, primary_key=True)
    titel = models.CharField("Titel", max_length=20)

    '''
    The one underscores are to define attribute "passwort" as private
    '''
    _passwort = models.CharField("Passwort", max_length=20)

    '''
    To check whether the account exists and the passwort is valid
    If the passwort is valid, this method will return true; otherwise false
    '''

    '''
    To get the private attribute __passwort outside this class
    '''

    @property
    def passwort(self):
        return self._passwort

    '''
    To reset the passwort
    '''

    @passwort.setter
    def passwort(self, new_passwort):
        self._passwort = new_passwort

    def __str__(self):
        return self.mail_address


class Study(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name = models.CharField("Study name", max_length=30)
    start_date_time = models.DateTimeField("Start time")
    end_date_time = models.DateTimeField("End time")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "studies"


class Questionnaire(models.Model):
    study = models.ForeignKey(Study, on_delete=models.CASCADE, null=True)
    name = models.CharField("Questionnaire name", max_length=30)
    due_after = models.DurationField(
        "Valid time duration after displayed, in [DD] [HH:[MM:]]ss format", null=True)
    max_trigger_times_per_day = models.PositiveIntegerField(
        "Maximal number the questionnaire can be displayed per day", null=True)

    def __str__(self):
        return self.name


class TriggerEvent(models.Model):
    # The choices of the trigger events
    TRIGGER_EVENT_CHOICES = (
        ('Acc', 'Accelerometer'),
        ('Li_Acc', 'Linear Acceleration'),
        ('Grav', 'Gravity'),
        ('Rota', 'Rotation Vector'),
        ('Tem', 'Temperature'),
        ('Light', 'Light'),
        ('Pres', 'Pressure'),
        ('Hum', 'Relative Humidity'),
        ('Mag', 'Magnetic Field'),
        ('Prox', 'Proximity'),
    )
    questionnaire_id = models.ForeignKey('Questionnaire', on_delete=models.CASCADE, null=True)
    name = models.CharField("Trigger Event Name", max_length=10, choices=TRIGGER_EVENT_CHOICES)
    value = models.CharField("Value", max_length=50)

    def __str__(self):
        return self.name

'''
The parent class of all the question classes
It contains the common attributes study_director_id, study_id, questionnaire_id, question_type and question_content
'''


class Question(models.Model):
    QUESTION_TYPE_CHOICES = (
        ('Text', 'Text Question'),
        ('Scale', 'Scale Question'),
        ('Choice', 'Choice Question'),
    )
    study_director_id = models.ForeignKey('StudyDirector', on_delete=models.CASCADE, null=True)
    study_id = models.ForeignKey('Study', on_delete=models.CASCADE, null=True)
    questionnaire_id = models.ForeignKey('Questionnaire', on_delete=models.CASCADE, null=True)
    question_type = models.CharField("Question Type", max_length=6, choices=QUESTION_TYPE_CHOICES)
    question_content = models.TextField("Question Content")
    options = models.TextField("Option")
    min_value = models.FloatField("Minimum")
    max_value = models.FloatField("Maximum")
    gap_value = models.FloatField("Gap")

    def __str__(self):
        return self.question_content

class Answer(models.Model):
    proband_id = models.ForeignKey('Proband', null=True)
    submit_date_time = models.DateTimeField("Submit Date and Time", null=True)
    question_id = models.IntegerField("Question ID", null=True)
    question_type = models.CharField("Question Type", max_length=30)
    text_value = models.TextField("Answer of Text Question", blank=True)
    choice_value = models.CharField("Answer of Choice Question", max_length=30)
    integer_value = models.FloatField("Answer of Scale Question")

    def __str__(self):
        return self.text_value


class Proband(models.Model):
    study_director_id = models.ForeignKey('StudyDirector', on_delete=models.CASCADE, null=True)
    study_id = models.ForeignKey('Study', on_delete=models.CASCADE, null=True)


class NotAnsweredQuestionnaire(models.Model):
    # This attribute represents the proband ID
    proband_id = models.ForeignKey('Proband', on_delete=models.CASCADE, null=True)
    questionnaire_id = models.ForeignKey('Questionnaire', on_delete=models.CASCADE, null=True)


class PersonalInformation(models.Model):
    proband_id = models.ForeignKey('Proband', on_delete=models.CASCADE, null=True)
    personal_information_name = models.CharField(max_length=30)
    string_value = models.CharField(max_length=30)
    integer_value = models.IntegerField()
