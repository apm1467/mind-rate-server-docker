from django.db import models
from django.core.exceptions import ObjectDoesNotExist

'''
CAUTION: when initializing an instance of this class, be sure to catch the IntegrityError, which is caused by a duplicate of primary key "mail_address" in table StudyDirector
'''

#TODO Set all all the  attribute to blank=True. After test they should be modified accordingly
#TODO Set StudyDirector.mail_address  "default=haha@gmail.com"

class StudyDirector(models.Model):
    '''
    To check whether the mail address is validated
    An unvalid mail address will cause ValidationError
    '''
    mail_address = models.EmailField("Email-Address", max_length=50, primary_key=True, blank=True, default="haha@gmail.com")
    titel = models.CharField("Titel", max_length=20, blank=True)

    '''
    The two underscores are to define attribute "passwort" as private
    '''
    _passwort = models.CharField("Passwort", max_length=20, blank=True)

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


class Study(models.Model):
    study_director_id = models.ForeignKey('StudyDirector', on_delete=models.CASCADE, null=True, blank=True, default="haha@gmail.com")
    study_name = models.CharField("Study Name", max_length=30, blank=True)
    start_date_time = models.DateTimeField("Start Date and Time", blank=True)
    end_date_time = models.DateTimeField("End Date and Time", blank=True)

    '''
    This method has overriden the original save method
    A new record of study will be saved if there is no duplicate of the study name
    The *args and **kwargs are for the future extension of the method
    '''

    def save(self, *args, **kwargs):
        if self.find_duplicate_name():
            super().save()

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


'''
This class takes a serial integer as primary key
'''


class Questionnaire(models.Model):
    study_director_id = models.ForeignKey('StudyDirector', on_delete=models.CASCADE, blank=True, null=True)
    study_id = models.ForeignKey('Study', on_delete=models.CASCADE, null=True, blank=True)
    questionnaire_name = models.CharField("Questionnaire Name", max_length=30, blank=True)
    submit_date_time = models.DateTimeField("Deadline Date and Time", null=True, blank=True)

    '''
    This method has overriden the original save method
    A new record of questionnaire will be saved if there is no duplicate of the questionnaire name
    The *args and **kwargs are for the future extension of the method
    '''

    def save(self, *args, **kwargs):
        if self.find_duplicate_name():
            super().save()

    '''
    The method is to find out whether there is a duplicate of the questionnaire name in the same studies of the same study director
    This method will return true if NO duplicate is found; otherwise false
    '''

    def find_duplicate_name(self):
        try:
            Study.objects.get(study_director_id=self.study_director_id, study_id=self.study_id,
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
    questionnaire_id = models.ForeignKey('Questionnaire', on_delete=models.CASCADE, blank=True)
    name = models.CharField("Trigger Event Name", max_length=10, choices=TRIGGER_EVENT_CHOICES, blank=True)
    value = models.CharField("Value", max_length=30, blank=True)


'''
The parent class of all the question classes
It contains the common attributes study_director_id, study_id, questionnaire_id, question_type and question_content
'''


class CommonQuestion(models.Model):
    study_director_id = models.ForeignKey('StudyDirector', on_delete=models.CASCADE, null=True, blank=True)
    study_id = models.ForeignKey('Study', on_delete=models.CASCADE, null=True, blank=True)
    questionnaire_id = models.ForeignKey('Questionnaire', on_delete=models.CASCADE, null=True, blank=True)
    question_type = models.CharField("Question Type", max_length=30, blank=True)
    question_content = models.TextField("Question Content", blank=True)

    class Meta:
        abstract = True


class TextQuestion(CommonQuestion):
    # Nothing should be defined here
    pass


class ChoiceQuestion(CommonQuestion):
    """
    To stored the options, different options will be separated by semicolon
    """
    option = models.TextField("Option", blank=True)


class ScaleQuestion(CommonQuestion):
    min_value = models.FloatField("Minimum", blank=True)
    max_value = models.FloatField("Maximum", blank=True)
    gap_value = models.FloatField("Gap", blank=True)


class Answer(models.Model):
    study_director_id = models.ForeignKey('StudyDirector', on_delete=models.CASCADE, null=True, blank=True)
    study_id = models.ForeignKey('Study', on_delete=models.CASCADE, null=True, blank=True)
    questionnaire_id = models.ForeignKey('Questionnaire', on_delete=models.CASCADE, null=True, blank=True)
    question_id = models.IntegerField('Question', null=True, blank=True)
    proband_id = models.IntegerField(blank=True)
    submit_date_time = models.DateTimeField("Submit Date and Time", blank=True)
    question_type = models.CharField("Question Type", max_length=30, blank=True)
    text_value = models.TextField("Answer of Text Question", blank=True)
    choice_value = models.CharField("Answer of Choice Question", max_length=30, blank=True)
    integer_value = models.FloatField("Answer of Scale Question", blank=True)


class Proband(models.Model):
    study_director_id = models.ForeignKey('StudyDirector', on_delete=models.CASCADE, null=True, blank=True)
    study_id = models.ForeignKey('Study', on_delete=models.CASCADE, null=True, blank=True)


class NotAnsweredQuestionnaire(models.Model):
    # This attribute represents the proband ID
    proband_id = models.ForeignKey('Proband', on_delete=models.CASCADE, null=True, blank=True)
    questionnaire_id = models.ForeignKey('Questionnaire', on_delete=models.CASCADE, null=True, blank=True)


class PersonalInformation(models.Model):
    proband_id = models.ForeignKey('Proband', on_delete=models.CASCADE, null=True, blank=True)
    personal_information_name = models.CharField(max_length=30, blank=True)
    string_value = models.CharField(max_length=30, blank=True)
    integer_value = models.IntegerField(blank=True)
