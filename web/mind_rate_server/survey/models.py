from django.db import models
from django.core.exceptions import ObjectDoesNotExist

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
    study_director_id = models.ForeignKey('StudyDirector', on_delete=models.CASCADE, null=True)
    study_name = models.CharField("Study Name", max_length=30)
    #start_date_time = models.DateTimeField("Start Date and Time")
    #end_date_time = models.DateTimeField("End Date and Time")

    '''
    This method has overriden the original save method
    A new record of study will be saved if there is no duplicate of the study name
    The *args and **kwargs are for the future extension of the method
    '''

    def save(self, *args, **kwargs):
        if self.find_duplicate_name():
            super(Study, self).save(*args, **kwargs)

    '''
    This method is to find out whether there is a duplicate of the study name in the studies of the same study director
    This method will return true if NO duplicate is found; otherwise false
    '''

    def find_duplicate_name(self):
        try:
            Study.objects.get(study_director_id=self.study_director_id, study_name=self.study_name)
        except ObjectDoesNotExist:
            return True
        return False

    def __str__(self):
        return self.study_name


'''
This class takes a serial integer as primary key
'''


class Questionnaire(models.Model):
    study_director_id = models.ForeignKey('StudyDirector', on_delete=models.CASCADE, null=True)
    study_id = models.ForeignKey('Study', on_delete=models.CASCADE, null=True)
    questionnaire_name = models.CharField("Questionnaire Name", max_length=30)
    # required_submit_date_time = models.DateTimeField("Deadline Date and Time", null=True)
    max_show_up_times_per_day = models.IntegerField("Max Show Up Times Per Day", null=True)

    '''
    This method has overriden the original save method
    A new record of questionnaire will be saved if there is no duplicate of the questionnaire name
    The *args and **kwargs are for the future extension of the method
    '''

    def save(self, *args, **kwargs):
        if self.find_duplicate_name():
            super(Questionnaire, self).save(*args, **kwargs)

    '''
    The method is to find out whether there is a duplicate of the questionnaire name in the same studies of the same study director
    This method will return true if NO duplicate is found; otherwise false
    '''

    def find_duplicate_name(self):
        try:
            Questionnaire.objects.get(study_director_id=self.study_director_id, study_id=self.study_id,
                              questionnaire_name=self.questionnaire_name)
        except ObjectDoesNotExist:
            return True
        return False

    '''
    This method will take a dictionary as parameter and set the trigger events of the questionnaire accordingly
    The keys in the dictionary represent the name of trigger event, the values represent the parameter for the trigger event
    '''

    def set_trigger_event(self, trigger_events_dic):
        for k, v in trigger_events_dic.iteritems():
            t = TriggerEvent(trigger_events_id=self.id, name=k, value=v)
            t.save()

    def __str__(self):
        return self.questionnaire_name


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
