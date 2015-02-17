from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class AccountManager(BaseUserManager):
	def create_user(self, email, password=None, **kwargs):
		if not email:
			raise ValueError("User must be have a valid Email Address")
		if not kwargs.get('username'):
			raise ValueError("User must have a valid Username")
		if not kwargs.get('teaching_institution'):
			raise ValueError('User must have a valid Teaching Institution')
		if not kwargs.get('first_name'):
			raise ValueError('User must have a valid First Name')
		if not kwargs.get('last_name'):
			raise ValueError('User must have a valid Last Name')

		account = self.model(
			email=self.normalize_email(email),
			username=kwargs.get('username'),
			teaching_institution=kwargs.get('teaching_institution'),
			first_name=kwargs.get('first_name'),
			last_name=kwargs.get('last_name'))

		account.set_password(password)
		account.save()

		return account

	def create_superuser(self, email, password, **kwargs):
		account = self.create_user(email, password, **kwargs)
		account.is_admin = True
		account.save()

		return account

class Account(AbstractBaseUser):
	email = models.EmailField(unique=True)
	username = models.CharField(max_length=40, unique=True)

	first_name = models.CharField(max_length=40)
	last_name = models.CharField(max_length=40)

	teaching_institution = models.CharField(max_length=140)

	is_admin = models.BooleanField(default=False)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	objects = AccountManager()

	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'teaching_institution']

	def __unicode__(self):
		return self.email

	def get_full_name(self):
		return ' '.join([self.first_name, self.last_name])

	def get_short_name(self):
		return self.first_name

	def get_teaching_institution(self):
		return self.teaching_institution