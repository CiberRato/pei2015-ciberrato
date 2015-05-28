from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import uuid

from django.core.validators import MinValueValidator, MinLengthValidator, EmailValidator
from ciberonline.validators import validate_word


class AccountManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        """
        Create an user, with email, username, teaching institution, first name, last name and password
        """
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
        """
        Create a superuser, with email, username, teaching institution, first name, last name, password and is_admin == True
        """
        account = self.create_user(email, password, **kwargs)
        account.is_superuser = True
        account.is_staff = True
        account.save()

        return account


class Account(AbstractBaseUser):
    email = models.EmailField(unique=True, blank=False, validators=[EmailValidator])
    username = models.CharField(max_length=40, unique=True, blank=False,
                                validators=[validate_word, MinLengthValidator(2)])

    first_name = models.CharField(max_length=40, validators=[MinLengthValidator(2)])
    last_name = models.CharField(max_length=40, validators=[MinLengthValidator(2)])

    teaching_institution = models.CharField(max_length=140, validators=[MinLengthValidator(2)])

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False, blank=False)
    is_superuser = models.BooleanField(default=False, blank=False)
    teams = models.ManyToManyField('Team', through='TeamMember', related_name="account")

    login_error = models.BooleanField(default=False)

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


class EmailToken(models.Model):
    token = models.CharField(max_length=100, blank=False, unique=True, default=uuid.uuid4)
    user = models.ForeignKey(Account, blank=False)

    class Meta:
        unique_together = ('token', 'user',)

""" GROUP MODELS """


class Team(models.Model):
    name = models.CharField(max_length=128, unique=True, blank=False, validators=[validate_word, MinLengthValidator(1)])
    max_members = models.IntegerField(default=5, validators=[MinValueValidator(1)])

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name


class TeamMember(models.Model):
    account = models.ForeignKey(Account, blank=False)
    team = models.ForeignKey(Team, blank=False)
    is_admin = models.BooleanField(default=False)

    class Meta:
        unique_together = ('account', 'team',)

    def __unicode__(self):
        return "%s is in team %s (as %s)" % (self.account, self.team, self.is_admin)
