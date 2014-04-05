from hashlib import md5
from datetime import timedelta
from calendar import monthrange

from django.db import (
    connection,
    models,
)
from django.conf import settings
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
    (0, 'change_email', _('Change email')),
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
        return user

    def random_users(self, count=4):
        users = self.raw(
            '''
            SELECT u.*,
            (SELECT COUNT(id) FROM caffeine_caffeine
             WHERE u.id=user_id AND ctype={0:d}) AS coffees,
            (SELECT COUNT(id) FROM caffeine_caffeine
             WHERE u.id=user_id AND ctype={1:d}) AS mate
            FROM caffeine_user u ORDER BY RAND() LIMIT {2:d}
            '''.format(DRINK_TYPES.coffee, DRINK_TYPES.mate, count))
        return users

    def recently_joined(self, count=5):
        return self.order_by('-date_joined')[:count]

    def longest_joined(self, count=5):
        return self.order_by('date_joined')[:count]


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

    def __unicode__(self):
        return self.get_full_name()


def hour_result_dict():
    return {
        'labels': [unicode(i) for i in range(24)],
        'coffee': [0 for i in range(24)],
        'mate': [0 for i in range(24)],
        'maxvalue': 1,
    }


def month_result_dict(date):
    result = {
        'labels': [unicode(i + 1) for i in range(monthrange(
            date.year, date.month)[1])],
    }
    result.update({
        'coffee': [0 for i in range(len(result['labels']))],
        'mate': [0 for i in range(len(result['labels']))],
        'maxvalue': 1,
    })
    return result


def year_result_dict():
    return {
        'labels': [unicode(i + 1) for i in range(12)],
        'coffee': [0 for i in range(12)],
        'mate': [0 for i in range(12)],
        'maxvalue': 1,
    }


def weekdaily_result_dict():
    result = {
        'labels': [_('Mon'), _('Tue'), _('Wed'), _('Thu'), _('Fri'),
                   _('Sat'), _('Sun')]
    }
    result.update({
        'coffee': [0 for i in range(len(result['labels']))],
        'mate': [0 for i in range(len(result['labels']))],
        'maxvalue': 1,
    })
    return result


class CaffeineManager(models.Manager):
    """
    Manager class for Caffeine.

    """
    def total_caffeine_for_user(self, user):
        """
        Return total coffees for user profile.

        :param User user: user instance
        :return: result dictionary
        """
        q = self.filter(user=user).values('ctype').annotate(
            num_drinks=models.Count('ctype'))
        result = {
            DRINK_TYPES.mate: 0,
            DRINK_TYPES.coffee: 0,
        }
        for item in q:
            result[item['ctype']] = item['num_drinks']
        return result

    def latest_caffeine_for_user(self, user, count=10):
        """
        Return the latest caffeine entries for the given user.

        :param User user: user instance
        :param int count: number of entries
        :return: list of Caffeine instances
        """
        return self.filter(user=user).order_by('-entrytime')[:count]

    def hourly_caffeine_for_user(self, user):
        """
        Return series of hourly coffees and mate on current day for user
        profile.

        :param User user: user instance
        :return: result dictionary
        """
        result = hour_result_dict()
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT ctype, COUNT(id) AS value,
                   DATE_FORMAT(date, '%%H') AS hour
            FROM   caffeine_caffeine
            WHERE  DATE_FORMAT(CURRENT_TIMESTAMP, '%%Y-%%m-%%d') =
                   DATE_FORMAT(date, '%%Y-%%m-%%d')
                   AND user_id = {0:d}
            GROUP BY hour, ctype
            """.format(user.id))
        for ctype, value, hour in cursor.fetchall():
            result['maxvalue'] = max(value, result['maxvalue'])
            result[DRINK_TYPES._triples[ctype][1]][int(hour)] = value
        return result

    def daily_caffeine_for_user(self, user):
        """
        Return series of daily coffees and mate in current month for user
        profile.

        :param User user: user instance
        :return: result dictionary
        """
        result = month_result_dict(timezone.now())
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT ctype, COUNT(id) AS value,
                   DATE_FORMAT(date, '%%d') AS day
            FROM   caffeine_caffeine
            WHERE  DATE_FORMAT(CURRENT_TIMESTAMP, '%%Y-%%m') =
                   DATE_FORMAT(date, '%%Y-%%m')
                   AND user_id = {0:d}
            GROUP BY day, ctype
            """.format(user.id))
        for ctype, value, day in cursor.fetchall():
            result['maxvalue'] = max(value, result['maxvalue'])
            result[DRINK_TYPES._triples[ctype][1]][int(day) - 1] = value
        return result

    def monthly_caffeine_for_user(self, user):
        """
        Return a series of monthly coffees and mate in current month for user
        profile.

        :param User user: user instance
        :return: result dictionary
        """
        result = year_result_dict()
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT ctype, COUNT(id) AS value,
                   DATE_FORMAT(date, '%%m') AS month
            FROM   caffeine_caffeine
            WHERE  DATE_FORMAT(CURRENT_TIMESTAMP, '%%Y') =
                   DATE_FORMAT(date, '%%Y')
                   AND user_id = {0:d}
            GROUP BY month, ctype
            """.format(user.id))
        for ctype, value, month in cursor.fetchall():
            result['maxvalue'] = max(value, result['maxvalue'])
            result[DRINK_TYPES._triples[ctype][1]][int(month) - 1] = value
        return result

    def hourly_caffeine_for_user_overall(self, user):
        """
        Return a series of hourly caffeinated drinks for the whole timespan of
        a user's membership.

        :param User user: user instance
        :return: result dictionary
        """
        result = hour_result_dict()
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT ctype, COUNT(id) AS value,
                   DATE_FORMAT(date, '%%H') AS hour
            FROM   caffeine_caffeine
            WHERE  user_id = {0:d}
            GROUP BY hour, ctype
            """.format(user.id))
        for ctype, value, hour in cursor.fetchall():
            result['maxvalue'] = max(value, result['maxvalue'])
            result[DRINK_TYPES._triples[ctype][1]][int(hour)] = value
        return result

    def weekdaily_caffeine_for_user_overall(self, user):
        """
        Return a series of caffeinated drinks per weekday for the whole
        timespan of a user's membership.

        :param User user: user instance
        :return: result dictionary
        """
        result = weekdaily_result_dict()
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT ctype, COUNT(id) AS value,
                   DATE_FORMAT(date, '%%a') AS wday
            FROM   caffeine_caffeine
            WHERE  user_id = {0:d}
            GROUP BY wday, ctype
            """.format(user.id))
        for ctype, value, wday in cursor.fetchall():
            result['maxvalue'] = max(value, result['maxvalue'])
            result[DRINK_TYPES._triples[ctype][1]][
                result['labels'].index(wday)] = value
        return result

    def find_recent_caffeine(self, user, date, ctype):
        caffeines = self.filter(
            user=user, ctype=ctype,
            date__gte=(date - timedelta(
                minutes=settings.MINIMUM_DRINK_DISTANCE)))
        try:
            return caffeines.latest('date')
        except Caffeine.DoesNotExist:
            return False

    def latest_caffeine_activity(self, count=10):
        return self.order_by('-date').select_related('user')[:count].all()

    def top_consumers_total(self, ctype, count=10):
        q = self.filter(ctype=ctype).select_related('user').values_list(
            'user').annotate(caffeine_count=models.Count('id')).order_by(
            '-caffeine_count')[:count]
        users = User.objects.in_bulk([user for user, caffeine_count in q])
        result = []
        for user_id, caffeine_count in q:
            result.append({'user': users[user_id],
                           'caffeine_count': caffeine_count})
        return result

    def top_consumers_average(self, ctype, count=10):
        result = []
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT c.user_id,
                   COUNT(c.id) / (DATEDIFF(
                       CURRENT_DATE, MIN(c.date)) + 1) AS average
            FROM   caffeine_caffeine c JOIN caffeine_user u ON
                   c.user_id = u.id
            WHERE  c.ctype = {0:d}
            GROUP BY c.user_id
            ORDER BY average DESC
            LIMIT {1:d}
            """.format(ctype, count))
        q = cursor.fetchall()
        users = User.objects.in_bulk([row[0] for row in q])
        for user_id, average in q:
            result.append({'user': users[user_id],
                           'average': average})
        return result


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

    objects = CaffeineManager()

    class Meta:
        ordering = ['-date']

    def __unicode__(self):
        return (
            "%s at %s %s" % (
                DRINK_TYPES[self.ctype][1],
                self.date,
                self.timezone or "")).strip()

    def format_type(self):
        return DRINK_TYPES[self.ctype][1]


class ActionManager(models.Manager):
    """
    Manager class for actions.

    """
    def create_action(self, user, actiontype, data, validdays):
        action = self.model(user=user, atype=actiontype, data=data)
        action.validuntil = timezone.now() + timedelta(validdays)
        action.code = md5(user.username +
                          ACTION_TYPES[actiontype][1] +
                          data +
                          action.validuntil.strftime(
                              "%Y%m%d%H%M%S%f")).hexdigest()
        action.save(using=self.db)
        return action


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

    objects = ActionManager()

    class Meta:
        ordering = ['-validuntil']

    def __unicode__(self):
        return "%s valid until %s" % (ACTION_TYPES[self.atype][1],
                                      self.validuntil)
