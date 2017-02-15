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
        "(Optional) Valid time duration after displayed, in [DD] [HH:[MM:]]ss format, default unlimited time",
        null=True, blank=True)
    max_trigger_times_per_day = models.PositiveIntegerField(
        "Maximal number the questionnaire can be displayed per day", null=True)

    def __str__(self):
        return self.name


class TriggerEvent(models.Model):
    questionnaire = models.OneToOneField(Questionnaire, on_delete=models.CASCADE, null=True)
    min_time_space = models.DurationField(
        "Minimal time space between two trigger events, in [DD] [HH:[MM:]]ss format", null=True)

    # trigger options based on time
    datetime = models.DateTimeField("(Optional) Triggered at a specific combination of a date and a time",
                                    null=True, blank=True)
    time = models.TimeField("(Optional) Triggered at a time, independent of any particular day",
                            null=True, blank=True)

    # trigger options that return Boolean values
    triggeredWhenCalendarEventBegins = models.BooleanField("Triggered when a event on Android calendar begins",
                                                           default=False)
    triggeredWhenCalendarEventEnds = models.BooleanField("Triggered when a event on Android calendar ends",
                                                         default=False)
    triggeredWhenFacebookNotificationComes = models.BooleanField("Triggered each time a Facebook notification comes",
                                                                 default=False)
    triggeredWhenWhatsAppNotificationComes = models.BooleanField("Triggered each time a WhatsApp notification comes",
                                                                 default=False)
    triggeredWhenSmsComes = models.BooleanField("Triggered each time a SMS comes", default=False)
    triggeredWhenPhoneCallEnds = models.BooleanField("Triggered each time a phone call ends", default=False)

    # trigger option based on Android user activity API
    IN_VEHICLE = "IN_VEHICLE"
    ON_BICYCLE = "ON_BICYCLE"
    ON_FOOT = "ON_FOOT"
    RUNNING = "RUNNING"
    STILL = "STILL"
    TILTING = "TILTING"
    UNKNOWN = "UNKNOWN"
    WALKING = "WALKING"
    USER_ACTIVITY_CHOICES = (
        (IN_VEHICLE, "The device is in a vehicle, such as a car"),
        (ON_BICYCLE, "The device is on a bicycle"),
        (ON_FOOT, "The device is on a user who is walking or running"),
        (RUNNING, "The device is on a user who is running"),
        (STILL, "The device is still (not moving)"),
        (TILTING, "The device angle relative to gravity changed significantly (tilting)"),
        (UNKNOWN, "Unable to detect the current activity"),
        (WALKING, "The device is on a user who is walking")
    )
    user_activity = models.CharField("(Optional) Triggered at a specific user activity",
                                     max_length=10, choices=USER_ACTIVITY_CHOICES, null=True, blank=True)

    # trigger options based on environment sensors
    VERY_HIGH = "VH"
    HIGH = "H"
    MEDIUM = "M"
    LOW = "L"
    VERY_LOW = "VL"
    SENSOR_LEVEL_CHOICES = (
        (VERY_HIGH, "very high"),
        (HIGH, "high"),
        (MEDIUM, "medium"),
        (LOW, "low"),
        (VERY_LOW, "very low")
    )
    light = models.CharField("(Optional) Triggered at a specific ambient light level",
                             max_length=2, choices=SENSOR_LEVEL_CHOICES, null=True, blank=True)
    relative_humidity = models.CharField("(Optional) Triggered at a specific relative humidity level",
                                         max_length=2, choices=SENSOR_LEVEL_CHOICES, null=True, blank=True)
    air_pressure = models.CharField("(Optional) Triggered at a specific air pressure level",
                                    max_length=2, choices=SENSOR_LEVEL_CHOICES, null=True, blank=True)
    linear_acceleration = models.CharField("(Optional) Triggered at a specific linear acceleration level",
                                           max_length=2, choices=SENSOR_LEVEL_CHOICES, null=True, blank=True)
    proximity = models.CharField("(Optional) Triggered at a specific proximity (distance) between user and device",
                                 max_length=2, choices=SENSOR_LEVEL_CHOICES, null=True, blank=True)

    def __str__(self):
        return "%s trigger event" % self.questionnaire.name

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
