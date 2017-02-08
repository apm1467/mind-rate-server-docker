from django.db import models
'''
The custom exceptions should be imported here
'''

class StudyDirector(models.Model):
	#the choices of appellation
	APPELLATION_CHOICES = (
		('Mr', 'Mr'),
		('Ms', 'Ms'),
	)
	#if the mail address is not validated, it will return ???
	mail_address = models.EmailField("Email-Address", max_length=50, primary_key=true)
	first_name = models.CharField("First Name", max_length=30)
	last_name = models.CharField("Last Name", max_length=30)
	titel = models.CharField("Titel", max_length=20)
	appellation = models.CharField("Appellation", max_length=2, choices=APPELLATION_CHOICES)
	#the two underscores are to define passwort as a private variable
	__passwort = models.CharField("Passwort", max_length=20)

class Study(models.Model):
	study_director_id = models.ForeignKey("Study Director", StudyDirector, on_delete=models.CASCADE)
	study_name = models.CharField("Study Name", max_length=30)
	start_date_time = models.DateTimeField()
	end_date_time = models.DateTimeField()

	'''
	A new record of study will be saved if there is no duplicate of the study name
	The *args and **kwargs are for the future extension of the method
	'''
	def save(self, *args, **kwargs):
		findDuplicateName()
		super(Study, self).save(*args, **kwargs)
			
	'''
	The method is to find out whether there is a duplicate of the study name in the studies of the same study director should be defined below
	This method will return true if NO duplicate is found; otherwise false
	'''
	def findDuplicateName(self):
		result = Study.objects.filter(study_director_id = self.study_director_id)
		if result.count() > 0:
			raise DuplicateExistsException("There is a duplicate study in the database!")
		else:
			return true
		
class Questionnaire(models.Model):
	study_director_id = models.ForeignKey("Study Director", StudyDirector, on_delete=models.CASCADE)
	study_id = models.ForeignKey(Study, on_delete=models.CASCADE)
	name = models.CharField(max_length=30)
	deadline_date_time = models.DateTimeField()

	'''
	A new record of questionnaire will be saved if there is no duplicate of the questionnaire name
	The *args and **kwargs are for the future extension of the method
	'''
	def save(self, *args, **kwargs):
		findDuplicateName()
		super(Questionnaire, self).save(*args, **kwargs)

	'''
	The method is to find out whether there is a duplicate of the study name in the studies of the same study director should be defined below
	This method will return true if NO duplicate is found; otherwise false
	'''
	def findDuplicateName(self):
		result = Study.objects.filter(study_director_id = self.study_director_id)
		if result.count() > 0:
			raise DuplicateExistsException("There is a duplicate study in the database!")
		else:
			return true

	'''
	The method will take a dictionary as parameter and set the trigger events of the questionnaire accordingly
	'''
	def setTriggerEvent(self, )

class TriggerEvent(models.Model):
	#This ID is related to the primary key of questionnaire
	trigger_events_id = models.ForeignKey(Questionnaire, on_delete=models.CASCADE)
	name = models.CharField(max_length=10)
	value = models.IntegerField()

'''
The parent class of all the question classes
It contains the common attributes study_director_id, study_id, questionnaire_id, question_type and question_content
'''
class CommonQuestion(models.Model):
	study_director_id = models.ForeignKey("Study Director ID", StudyDirector, on_delete=models.CASCADE)
	study_id = models.ForeignKey("Study ID", Study, on_delete=models.CASCADE)
	questionnaire_id = models.ForeignKey("Questionnaire ID", Questionnaire, on_delete=models.CASCADE)
	question_type = models.CharField("Question Type", max_length=30)
	question_content = models.TextField("Question Content")
	
	class Meta:
		abstract = True

class TextQuestion(CommonQuestion):
	#Nothing should be defined here
	pass

class ChoiceQuestion(CommonQuestion):
	'''
	To stored the options, different options will be separated by semicolon
	'''
	option = models.TextField("Option")

class ScaleQuestion(CommonQuestion):
	min_value = models.FloatField("Minimum")
	max_value = models.FloatField("Maximum")
	gap_value = models.FloatField("Gap")

class Answer(models.Model):
	study_director_id = models.ForeignKey(StudyDirector, on_delete=models.CASCADE)
	study_id = models.ForeignKey(Study, on_delete=models.CASCADE)
	questionnaire_id = models.ForeignKey(Questionnaire, on_delete=models.CASCADE)
	question_id = models.ForeignKey(Question, on_delete=models.CASCADE)
	proband_id = models.ForeignKey(Proband, on_delete=models.CASCADE)
	hand_up_date_time = models.DateTimeField()
	question_type = models.CharField(max_length=30)
	text_value = models.TextField()
	integer_value = models.IntegerField()

class Proband(models.Model):
	study_director_id = models.ForeignKey(StudyDirector, on_delete=models.CASCADE)
	study_id = models.ForeignKey(Study, on_delete=models.CASCADE)

class NotAnsweredQuestionnaires(models.Model):
	not_answered_questionnaires_id = models.ForeignKey(Proband, on_delete=models.CASCADE)
	questionnaire_id = models.ForeignKey(Questionnaire, on_delete=models.CASCADE)

class PersonalInformation(models.Model):
	personal_information_id = models.ForeignKey(Proband, on_delete=models.CASCADE)
	personal_information_name = models.CharField(max_length=10)
	string_value = models.CharField(max_length=30)
	integer_value = models.IntegerField()





























