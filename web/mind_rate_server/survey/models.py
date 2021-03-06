from django.db import models
from django.contrib.auth.models import User


class Study(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name = models.CharField("Study name", max_length=30)
    start_date_time = models.DateTimeField("Start time")
    end_date_time = models.DateTimeField("End time")
    answer_updated_times = models.PositiveIntegerField(default=0)

    def __str__(self):
        return "%s - ID: %d" % (self.name, self.id)

    class Meta:
        verbose_name_plural = "studies"


class ProbandInfoQuestionnaire(models.Model):
    study = models.OneToOneField(Study, on_delete=models.CASCADE, null=True)

    ask_for_birthday = models.BooleanField(default=False)
    ask_for_occupation = models.BooleanField(default=False)
    ask_for_gender = models.BooleanField(default=False)

    def __str__(self):
        return ""


class Questionnaire(models.Model):
    study = models.ForeignKey(Study, on_delete=models.CASCADE, null=True)
    name = models.CharField("(Optional) Questionnaire name", max_length=30, default="", null=True, blank=True)
    due_after = models.DurationField(
        "(Optional) Valid time duration after triggered; in [DD] [HH:[MM:]]ss format",
        null=True, blank=True, default="24:00:00")
    max_trigger_times_per_day = models.PositiveIntegerField("Maximal trigger times per day", default=50)

    def __str__(self):
        return self.name

    class Meta:
        order_with_respect_to = 'study'


class TriggerEvent(models.Model):
    questionnaire = models.OneToOneField(Questionnaire, on_delete=models.CASCADE, null=True)
    min_time_space = models.DurationField(
        "Minimal time space between two trigger events; in [HH:[MM:]]ss format", null=True, default="10:00")

    # trigger options based on time
    datetime = models.DateTimeField("(Optional) A specific date and time", null=True, blank=True)
    time = models.TimeField("(Optional) A specific time everyday", null=True, blank=True)

    # trigger options that return Boolean values
    triggeredWhenCalendarEventBegins = models.BooleanField("Triggered when a calendar event begins",
                                                           default=False)
    triggeredWhenCalendarEventEnds = models.BooleanField("Triggered when a calendar event ends",
                                                         default=False)
    triggeredWhenFacebookNotificationComes = models.BooleanField("Triggered when a Facebook notification comes",
                                                                 default=False)
    triggeredWhenWhatsAppNotificationComes = models.BooleanField("Triggered when a WhatsApp notification comes",
                                                                 default=False)
    triggeredWhenSmsComes = models.BooleanField("Triggered when a SMS comes", default=False)
    triggeredWhenPhoneCallEnds = models.BooleanField("Triggered when a phone call ends", default=False)

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
        (WALKING, "The device is on a user who is walking")
    )
    user_activity = models.CharField("(Optional) User activity",
                                     max_length=10, choices=USER_ACTIVITY_CHOICES, null=True, blank=True)

    # trigger options based on environment sensors
    VERY_HIGH = "VH"
    HIGH = "H"
    MEDIUM = "M"
    LOW = "L"
    VERY_LOW = "VL"
    AlWAYS = "AL"
    SENSOR_LEVEL_CHOICES = (
        (VERY_HIGH, "very high"),
        (HIGH, "high"),
        (MEDIUM, "medium"),
        (LOW, "low"),
        (VERY_LOW, "very low"),
        (AlWAYS, "all conditions")
    )
    light = models.CharField("(Optional) Light",
                             max_length=2, choices=SENSOR_LEVEL_CHOICES, null=True, blank=True)
    temperature = models.CharField("(Optional) Temperature",
                                   max_length=2, choices=SENSOR_LEVEL_CHOICES, null=True, blank=True)
    relative_humidity = models.CharField("(Optional) Relative humidity",
                                         max_length=2, choices=SENSOR_LEVEL_CHOICES, null=True, blank=True)
    air_pressure = models.CharField("(Optional) Air pressure",
                                    max_length=2, choices=SENSOR_LEVEL_CHOICES, null=True, blank=True)
    proximity = models.CharField("(Optional) Proximity (distance)",
                                 max_length=2, choices=SENSOR_LEVEL_CHOICES, null=True, blank=True)

    def __str__(self):
        return ""


class AbstractQuestion(models.Model):
    # belongs to either a normal questionnaire or a proband info questionnaire
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.CASCADE, null=True)
    proband_info_questionnaire = models.ForeignKey(ProbandInfoQuestionnaire, on_delete=models.CASCADE, null=True)

    question_text = models.CharField(max_length=200, null=True)
    show_by_default = models.BooleanField("Show by default (False if the question is hidden by default, and will only "
                                          "be showed to proband if it is triggered as a follow up question)",
                                          default=True)
    position = models.PositiveSmallIntegerField("Position", null=True)  # position on admin site

    def __str__(self):
        return self.question_text

    class Meta:
        abstract = True
        ordering = ['position']


class TextQuestion(AbstractQuestion):
    pass


class DragScaleQuestion(AbstractQuestion):
    min_value = models.FloatField(default=0)
    max_value = models.FloatField(default=10)


class SingleChoiceQuestion(AbstractQuestion):
    pass


class MultiChoiceQuestion(AbstractQuestion):
    pass


class ChoiceOption(models.Model):
    # this class is part of either a single or a multi question
    single_choice_question = models.ForeignKey(SingleChoiceQuestion, on_delete=models.DO_NOTHING, null=True)
    multi_choice_question = models.ForeignKey(MultiChoiceQuestion, on_delete=models.DO_NOTHING, null=True)

    # dirty hack as a work-around of the Grappelli drag-drop sorting bug
    # choice options can also be appended to a text or drag scale question;
    # they will then be seen as single choices questions
    text_question = models.ForeignKey(TextQuestion, on_delete=models.DO_NOTHING, null=True)
    drag_scale_question = models.ForeignKey(DragScaleQuestion, on_delete=models.DO_NOTHING, null=True)

    choice_text = models.CharField(max_length=200)
    next_question_position = models.PositiveSmallIntegerField("(Optional) Position of the follow up question",
                                                              null=True, blank=True)

    def belongs_to_single_choice_question(self):
        # exclude MultiChoiceQuestion
        if self.multi_choice_question is not None:
            return False
        else:
            return True

    def __str__(self):
        return self.choice_text


class Proband(models.Model):
    study = models.ForeignKey(Study, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.id


# simulation of a dictionary-like key-value pair for Proband
class ProbandInfoCell(models.Model):
    proband = models.ForeignKey(Proband, on_delete=models.CASCADE, null=True)
    key = models.CharField(max_length=200)
    value = models.CharField(max_length=200)


class QuestionnaireAnswer(models.Model):
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.CASCADE, null=True)
    submitter = models.ForeignKey(Proband, on_delete=models.CASCADE, null=True)
    submit_time = models.DateTimeField(null=True)

    class Meta:
        order_with_respect_to = 'questionnaire'


# simulation of a dictionary-like key-value pair for QuestionnaireAnswer
class SensorValueCell(models.Model):
    questionnaire_answer = models.ForeignKey(QuestionnaireAnswer, on_delete=models.CASCADE, null=True)
    key = models.CharField(max_length=200)
    value = models.CharField(max_length=200)


class AbstractQuestionAnswer(models.Model):
    questionnaire_answer = models.ForeignKey(QuestionnaireAnswer, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return "%s - Answer" % self.question.question_text

    class Meta:
        abstract = True


class TextQuestionAnswer(AbstractQuestionAnswer):
    question = models.ForeignKey(TextQuestion, on_delete=models.CASCADE, null=True)
    value = models.TextField(null=True)


class SingleChoiceQuestionAnswer(AbstractQuestionAnswer):
    question = models.ForeignKey(SingleChoiceQuestion, on_delete=models.CASCADE, null=True)
    value = models.TextField(null=True)


class MultiChoiceQuestionAnswer(AbstractQuestionAnswer):
    question = models.ForeignKey(MultiChoiceQuestion, on_delete=models.CASCADE, null=True)
    value = models.TextField(null=True)


class DragScaleQuestionAnswer(AbstractQuestionAnswer):
    question = models.ForeignKey(DragScaleQuestion, on_delete=models.CASCADE, null=True)
    value = models.TextField(null=True)
