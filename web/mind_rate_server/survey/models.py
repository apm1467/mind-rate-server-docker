from django.db import models

'''
CAUTION: when initializing an instance of this class, be sure to catch the IntegrityError, which is caused by a duplicate of primary key "mail_address" in table StudyDirector
'''
class StudyDirector(models.Model):
	'''
	The choices of appellation
	The first arguments in the brackets is the value that will be stored in the database
	The second one will be shown on the web app
	'''
	APPELLATION_CHOICES = (
		('Mr', 'Mr'),
		('Ms', 'Ms'),
	)

	'''
	To check whether the mail address is validated
	An unvalid mail address will cause ValidationError
	'''
	mail_address = models.EmailField("Email-Address", max_length=50, primary_key=True)
	first_name = models.CharField("First Name", max_length=30)
	last_name = models.CharField("Last Name", max_length=30)
	titel = models.CharField("Titel", max_length=20)
	appellation = models.CharField("Appellation", max_length=2, choices=APPELLATION_CHOICES)

	'''
	The two underscores are to define attribute "password" as private
	'''
	__password = models.CharField("Password", max_length=20)

	'''
	To check whether the account exists and the password is valid
	If the password is valid, this method will return True; otherwise False
	'''
	def signIn(self, sign_in_mail_address, password):
		try:
			existingAccount = StudyDirector.objects.get(mail_address = sign_in_mail_address)
			if password == existingAccount.password:
				return True
			else:
				return False
		except DoesNotExist:
			print "%s has not yet registered. You should sign up first." % sign_in_mail_address

	'''
	To get the private attribute __password outside this class
	'''
	@property
	def password(self):
		return self.__password

	'''
	To reset the password
	'''
	@password.setter
	def password(self, new_password):
		self.__password = new_password

class Study(models.Model):
	study_director_id = models.ForeignKey("Study Director", StudyDirector, on_delete=models.CASCADE)
	study_name = models.CharField("Study Name", max_length=30)
	start_date_time = models.DateTimeField("Start Date and Time")
	end_date_time = models.DateTimeField("End Date and Time")

	'''
	This method has overriden the original save method
	A new record of study will be saved if there is no duplicate of the study name
	The *args and **kwargs are for the future extension of the method
	'''
	def save(self, *args, **kwargs):
		if findDuplicateName():
			super(Study, self).save(*args, **kwargs)
			
	'''
	This method is to find out whether there is a duplicate of the study name in the studies of the same study director
	This method will return True if NO duplicate is found; otherwise False
	'''
	def findDuplicateName(self):
		try:
			Study.objects.get(study_director_id = self.study_director_id, study_name = self.study_name)
		except DoesNotExist:
			return True
		return False

'''
This class takes a serial integer as primary key
'''
class Questionnaire(models.Model):
	study_director_id = models.ForeignKey("Study Director", StudyDirector, on_delete=models.CASCADE)
	study_id = models.ForeignKey("Study", Study, on_delete=models.CASCADE)
	questionnaire_name = models.CharField("Questionnaire Name", max_length=30)
	deadline_date_time = models.DateTimeField("Deadline Date and Time")

	'''
	This method has overriden the original save method
	A new record of questionnaire will be saved if there is no duplicate of the questionnaire name
	The *args and **kwargs are for the future extension of the method
	'''
	def save(self, *args, **kwargs):
		if findDuplicateName():
			super(Study, self).save(*args, **kwargs)
			
	'''
	The method is to find out whether there is a duplicate of the questionnaire name in the same studies of the same study director
	This method will return True if NO duplicate is found; otherwise False
	'''
	def findDuplicateName(self):
		try:
			Study.objects.get(study_director_id = self.study_director_id, study_name = self.study_name, questionnaire_name = self.questionnaire_name)
		except DoesNotExist:
			return True
		return False

	'''
	This method will take a dictionary as parameter and set the trigger events of the questionnaire accordingly
	The keys in the dictionary represent the name of trigger event, the values represent the parameter for the trigger event
	'''
	def setTriggerEvent(self, trigger_events_dic):
		for k, v in trigger_events_dic.iteritems():
			t = TriggerEvent(trigger_events_id = self.id, name = k, value = v)
			t.save()

class TriggerEvent(models.Model):
	#The choices of the trigger events
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
	questionnaire_id = models.ForeignKey("Belongs to Questionnaire No.", Questionnaire, on_delete=models.CASCADE)
	name = models.CharField("Trigger Event Name", max_length=10, choices=TRIGGER_EVENT_CHOICES)
	value = models.CharField("Value", max_length=30)

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
	study_director_id = models.ForeignKey("Study Director ID", StudyDirector, on_delete=models.CASCADE)
	study_id = models.ForeignKey("Study ID", Study, on_delete=models.CASCADE)
	questionnaire_id = models.ForeignKey("Questionnaire ID", Questionnaire, on_delete=models.CASCADE)
	question_id = models.ForeignKey("Question", Question, on_delete=models.CASCADE)
	proband_id = models.ForeignKey("Proband", Proband, on_delete=models.CASCADE)
	hand_up_date_time = models.DateTimeField("Hand Up Date and Time")
	question_type = models.CharField("Question Type", max_length=30)
	text_value = models.TextField("Answer of Text Question")
	choice_value = models.CharField("Answer of Choice Question", max_length=30)
	integer_value = models.FloatField("Answer of Scale Question")

class Proband(models.Model):
	study_director_id = models.ForeignKey("Study Director ID", StudyDirector, on_delete=models.CASCADE)
	study_id = models.ForeignKey("Study ID", Study, on_delete=models.CASCADE)

class NotAnsweredQuestionnaire(models.Model):
	#This attribute represents the proband ID
	proband_id = models.ForeignKey("Belongs to Proband No.", Proband, on_delete=models.CASCADE)
	questionnaire_id = models.ForeignKey("Questionnaire ID", Questionnaire, on_delete=models.CASCADE)

class PersonalInformation(models.Model):
	proband_id = models.ForeignKey("Belongs to Proband No.", Proband, on_delete=models.CASCADE)
	personal_information_name = models.CharField(max_length=30)
	string_value = models.CharField(max_length=30)
	integer_value = models.IntegerField()





























