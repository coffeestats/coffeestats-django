from hashlib import md5

from django.db import models
from django.utils import timezone
from django.utils.http import urlquote
from django.utils.translation import ugettext as _
from django.contrib.auth.models import (
    AbstractUser,
    BaseUserManager,
)

from model_utils import Choices
from model_utils.fields import AutoCreatedField


DRINK_TYPES = Choices(
    (0, 'coffee', _('Coffee')),
    (1, 'mate', _('Mate')),
)

ACTION_TYPES = Choices(
    (1, 'change_email', _('Change email')),
)


class CaffeineUserManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        """
        Creates and saves a User with the given user name, email addresse and
        password.

        :param str username: the user name
        :param str email: the email address
        :param str password: the password
        :returns: User instance

        """
        if not username:
            raise ValueError(_("User must have a username."))
        if not email:
            raise ValueError(_("User must have an email address."))
        user = self.model(
            username=username,
            email=self.normalize_email(email))
        user.set_password(password)
        # on the run token
        # TODO: use something better for API authentication
        user.token = md5(username + password).hexdigest()
        user.date_joined = timezone.now()
        user.save(using=self.db)
        return user

    def create_superuser(self, username, email, password):
        """
        Creates and saves a superuser with the given user name, email address
        and password.

        """
        user = self.create_user(username, email, password)
        user.is_admin = True
        user.save(using=self.db)
        return User


class User(AbstractUser):
    """
    User model.

    """
    cryptsum = models.CharField(_('old password hash'),
                                max_length=60, blank=True)
    location = models.CharField(max_length=128, blank=True)
    public = models.BooleanField(default=True)
    token = models.CharField(max_length=32, unique=True)
    timezone = models.CharField(_('timezone'), max_length=40,
                                db_index=True, blank=True)

    objects = CaffeineUserManager()

    def get_absolute_url(self):
        return "/profile/?u=%s" % urlquote(self.username)


class Caffeine(models.Model):
    """
    Caffeinated drink model.

    """
    ctype = models.PositiveSmallIntegerField(choices=DRINK_TYPES,
                                             db_index=True)
    user = models.ForeignKey('User')
    date = models.DateTimeField(_('consumed'), db_index=True)
    entrytime = AutoCreatedField(_('entered'), db_index=True)
    timezone = models.CharField(max_length=40, db_index=True,
                                blank=True)

    class Meta:
        ordering = ['-date']

    def __unicode__(self):
        return "%s at %s" % (DRINK_TYPES[self.ctype][1], self.date)


class Action(models.Model):
    """
    Action model.

    """
    user = models.ForeignKey('User')
    code = models.CharField(_('action code'), max_length=32, unique=True)
    created = AutoCreatedField(_('created'))
    validuntil = models.DateTimeField(_('valid until'), db_index=True)
    atype = models.PositiveSmallIntegerField(_('action type'),
                                             choices=ACTION_TYPES,
                                             db_index=True)
    data = models.TextField(_('action data'))

    class Meta:
        ordering = ['-validuntil']

    def __unicode__(self):
        return "%s valid until %s" % (ACTION_TYPES[self.atype][1],
                                      self.validuntil)
