from hashlib import md5
from calendar import monthrange
from datetime import datetime, timedelta
import random

from django.conf import settings
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils import timezone


from caffeine.models import (
    ACTION_TYPES,
    Action,
    ActionManager,
    Caffeine,
    CaffeineManager,
    CaffeineUserManager,
    DRINK_TYPES,
    User,
    WEEKDAY_LABELS,
)


class CaffeineUserManagerTest(TestCase):

    def _populate_some_testusers(self):
        for num in range(10):
            User.objects.create(
                username='test{}'.format(num + 1),
                token='testtoken{}'.format(num + 1),
                date_joined=timezone.now() - timedelta(days=num))

    def test_create_user_empty_username(self):
        with self.assertRaisesRegexp(
                ValueError, 'User must have a username.'):
            User.objects.create_user('', '')

    def test_create_user_empty_email(self):
        with self.assertRaisesRegexp(
                ValueError, 'User must have an email address.'):
            User.objects.create_user('testuser', '')

    def test_create_user_with_no_password(self):
        user = User.objects.create_user('testuser', 'test@bla.com')
        self.assertEqual(user.token, '')

    def test_create_user_with_password(self):
        user = User.objects.create_user('testuser', 'test@bla.com', 'password')
        self.assertEqual(user.token, md5('testuserpassword').hexdigest())
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)
        self.assertTrue(user.public)

    def test_create_superuser(self):
        user = User.objects.create_superuser(
            'testadmin', 'admin@bla.com', 's3cr3t')
        self.assertEqual(user.token, md5('testadmins3cr3t').hexdigest())
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.public)

    def test_random_users_no_users(self):
        randomusers = [u for u in User.objects.random_users()]
        self.assertEqual(len(randomusers), 0)

    def test_random_users_existing_users(self):
        self._populate_some_testusers()
        randomusers = [u for u in User.objects.random_users()]
        self.assertEqual(len(randomusers), 4)

    def test_recently_joined(self):
        self._populate_some_testusers()
        users = [u.username for u in User.objects.recently_joined()]
        self.assertEqual(len(users), 5)
        self.assertEqual(users, ['test1', 'test2', 'test3', 'test4', 'test5'])

    def test_longest_joined(self):
        self._populate_some_testusers()
        users = [u.username for u in User.objects.longest_joined()]
        self.assertEqual(len(users), 5)
        self.assertEqual(users, ['test10', 'test9', 'test8', 'test7', 'test6'])

    def test_longest_joined_limit(self):
        self._populate_some_testusers()
        for u in User.objects.all():
            Caffeine.objects.create(user=u, ctype=DRINK_TYPES.coffee,
                                    date=u.date_joined, timezone=u.timezone)
        users = [u.username for u in User.objects.longest_joined(days=3)]
        self.assertEqual(len(users), 4)
        self.assertEqual(users, ['test4', 'test3', 'test2', 'test1'])


class UserTest(TestCase):

    def test_manager_is_caffeineusermanager(self):
        self.assertIsInstance(User.objects, CaffeineUserManager)

    def test_get_absolute_url(self):
        user = User.objects.create(username='testuser')
        self.assertEqual(user.get_absolute_url(), reverse(
            'public', kwargs={'username': 'testuser'}))

    def test___unicode__(self):
        user = User.objects.create(username='testuser')
        self.assertEqual(unicode(user), 'testuser')

        user = User.objects.create(username='testuser2', first_name='Test',
                                   last_name='User', token='foo')
        self.assertEqual(unicode(user), 'Test User')

    def test_export_csv(self):
        user = User.objects.create(username='testuser',
                                   email='testuser@bla.com')
        user.export_csv()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Your caffeine records')
        self.assertEqual(mail.outbox[0].body,
                         'Attached is your caffeine track record.')
        self.assertEqual(mail.outbox[0].recipients()[0], 'testuser@bla.com')
        self.assertEqual(len(mail.outbox[0].attachments), 2)
        self.assertRegexpMatches(mail.outbox[0].attachments[0][0],
                                 r'^coffee-.+\.csv$')
        self.assertRegexpMatches(mail.outbox[0].attachments[1][0],
                                 r'^mate-.+\.csv$')
        self.assertEqual(mail.outbox[0].attachments[0][2], 'text/csv')
        self.assertEqual(mail.outbox[0].attachments[1][2], 'text/csv')


class CaffeineManagerTest(TestCase):

    def _generate_caffeine_one_day(self, user):
        now = datetime.today()
        for hour in range(10, 18):
            coffeetime = datetime(
                now.year, now.month, now.day, hour)
            Caffeine.objects.create(ctype=DRINK_TYPES.coffee,
                                    date=coffeetime, user=user)
            if hour % 2 == 0:
                matetime = coffeetime + timedelta(minutes=30)
                Caffeine.objects.create(ctype=DRINK_TYPES.mate,
                                        date=matetime, user=user)

    def _generate_caffeine_one_month(self, user):
        now = datetime.today()
        labels = []
        for day in range(1, monthrange(now.year, now.month)[1] + 1):
            labels += [unicode(day)]
            for hour, drinktype in [
                (hour, list(DRINK_TYPES)[hour % len(DRINK_TYPES)][0])
                for hour in range(10, 18)
            ]:
                caffeinetime = datetime(
                    now.year, now.month, day, hour)
                Caffeine.objects.create(ctype=drinktype,
                                        date=caffeinetime, user=user)
        return labels

    def _generate_caffeine_one_year(self, user):
        for month in range(1, 13):
            now = datetime.now()
            for day in [
                random.randrange(monthrange(now.year, month)[1]) + 1
                for n in range(5)
            ]:
                for hour, drinktype in [
                    (hour, list(DRINK_TYPES)[hour % len(DRINK_TYPES)][0])
                    for hour in range(10, 18)
                ]:
                    caffeinetime = datetime(
                        now.year, month, day, hour)
                    Caffeine.objects.create(ctype=drinktype,
                                            date=caffeinetime, user=user)

    def _generate_random_caffeine_multiple(self, usercount, caffeineperuser):
        for user, drinktype in [
            (User.objects.create(username='test{}'.format(usernum + 1),
                                 token='foo{}'.format(usernum)),
             list(DRINK_TYPES)[usernum % len(DRINK_TYPES)][0])
                for usernum in range(usercount)]:
            now = datetime.now()

            for day in [random.randrange(100)
                        for item in range(caffeineperuser)]:
                caffeinetime = now - timedelta(days=day)
                Caffeine.objects.create(
                    user=user, ctype=drinktype, date=caffeinetime)

    def _create_random_caffeine(self, users, number, timespan):
        now = datetime.now()
        drinks = dict(
            [(drinktype[0], {
                'month': 12 * [0],
                'hour': 24 * [0],
                'wday': 7 * [0]
            }) for drinktype in DRINK_TYPES])
        maxval = {
            'month': 1, 'hour': 1, 'wday': 1}

        for timeoffset in [
            timedelta(days=random.randrange(timespan.days),
                      seconds=random.randrange(86400))
            for _ in range(number)
        ]:
            caffeinetime = now - timeoffset
            ctype = random.choice(list(DRINK_TYPES))[0]
            user = random.choice(users)
            Caffeine.objects.create(date=caffeinetime, user=user, ctype=ctype)
            drinks[ctype]['month'][caffeinetime.month - 1] += 1
            drinks[ctype]['hour'][caffeinetime.hour] += 1
            drinks[ctype]['wday'][caffeinetime.weekday()] += 1
        for drinktype, drinkdict in drinks.items():
            for key in drinkdict:
                maxval[key] = max(maxval[key], max(drinkdict[key]))
        return drinks, maxval

    def _create_users(self, count):
        return [
            User.objects.create(username='test{}'.format(usernum + 1),
                                token='foo{}'.format(usernum))
            for usernum in range(count)
        ]

    def test_total_caffeine_for_user(self):
        testuser = User.objects.create(username='testuser', token='foo')
        self._generate_caffeine_one_day(testuser)
        total = Caffeine.objects.total_caffeine_for_user(testuser)
        self.assertEqual(len(total.keys()), len(DRINK_TYPES))
        self.assertEqual(total[DRINK_TYPES.coffee], 8)
        self.assertEqual(total[DRINK_TYPES.mate], 4)

    def test_total_caffeine(self):
        self._generate_random_caffeine_multiple(6, 10)
        total = Caffeine.objects.total_caffeine()
        self.assertEqual(len(total.keys()), len(DRINK_TYPES))
        self.assertEqual(total[DRINK_TYPES.coffee], 30)
        self.assertEqual(total[DRINK_TYPES.mate], 30)

    def test_latest_caffeine_for_user(self):
        testuser = User.objects.create(username='testuser', token='foo')
        self._generate_caffeine_one_day(testuser)
        latest = Caffeine.objects.latest_caffeine_for_user(user=testuser)
        self.assertEqual(len(latest), 10)
        self.assertEqual(len([
            drink for drink in latest
            if drink.ctype == DRINK_TYPES.coffee]), 7)
        self.assertEqual(len([
            drink for drink in latest
            if drink.ctype == DRINK_TYPES.mate]), 3)
        previous = latest[0].entrytime
        for drink in latest[1:]:
            self.assertTrue(drink.entrytime <= previous)
            previous = drink.entrytime

    def test_hourly_caffeine_for_user(self):
        testuser = User.objects.create(username='testuser', token='foo')
        self._generate_caffeine_one_day(testuser)
        hourly_caffeine = Caffeine.objects.hourly_caffeine_for_user(
            user=testuser)
        self.assertEqual(hourly_caffeine['maxvalue'], 1)
        self.assertEqual(hourly_caffeine['labels'],
                         [unicode(i) for i in range(24)])
        self.assertEqual(hourly_caffeine['coffee'],
                         10 * [0] + 8 * [1] + 6 * [0])
        self.assertEqual(hourly_caffeine['mate'],
                         10 * [0] + 4 * [1, 0] + 6 * [0])

    def test_hourly_caffeine(self):
        for user in self._create_users(5):
            self._generate_caffeine_one_day(user)
        hourly_caffeine = Caffeine.objects.hourly_caffeine()
        self.assertEqual(hourly_caffeine['maxvalue'], 5)
        self.assertEqual(hourly_caffeine['labels'],
                         [unicode(i) for i in range(24)])
        self.assertEqual(hourly_caffeine['coffee'],
                         10 * [0] + 8 * [5] + 6 * [0])
        self.assertEqual(hourly_caffeine['mate'],
                         10 * [0] + 4 * [5, 0] + 6 * [0])

    def test_daily_caffeine_for_user(self):
        testuser = User.objects.create(username='testuser', token='foo')
        labels = self._generate_caffeine_one_month(testuser)
        daily_caffeine = Caffeine.objects.daily_caffeine_for_user(testuser)
        self.assertEqual(daily_caffeine['maxvalue'], 4)
        self.assertEqual(daily_caffeine['labels'], labels)
        self.assertEqual(daily_caffeine['coffee'], len(labels) * [4])
        self.assertEqual(daily_caffeine['mate'], len(labels) * [4])

    def test_daily_caffeine(self):
        for user in self._create_users(5):
            labels = self._generate_caffeine_one_month(user)
        daily_caffeine = Caffeine.objects.daily_caffeine()
        self.assertEqual(daily_caffeine['maxvalue'], 20)
        self.assertEqual(daily_caffeine['labels'], labels)
        self.assertEqual(daily_caffeine['coffee'], len(labels) * [20])
        self.assertEqual(daily_caffeine['mate'], len(labels) * [20])

    def test_monthly_caffeine_for_user(self):
        testuser = User.objects.create(username='testuser', token='foo')
        self._generate_caffeine_one_year(user=testuser)
        monthly_caffeine = Caffeine.objects.monthly_caffeine_for_user(
            user=testuser)
        self.assertEqual(monthly_caffeine['maxvalue'], 20)
        self.assertEqual(monthly_caffeine['labels'],
                         [unicode(month) for month in range(1, 13)])
        self.assertEqual(monthly_caffeine['coffee'], 12 * [20])
        self.assertEqual(monthly_caffeine['mate'], 12 * [20])

    def test_monthly_caffeine_overall(self):
        for user in self._create_users(2):
            self._generate_caffeine_one_year(user=user)
        monthly_caffeine = Caffeine.objects.monthly_caffeine_overall()
        self.assertEqual(monthly_caffeine['maxvalue'], 40)
        self.assertEqual(monthly_caffeine['labels'],
                         [unicode(month) for month in range(1, 13)])
        self.assertEqual(monthly_caffeine['coffee'], 12 * [40])
        self.assertEqual(monthly_caffeine['mate'], 12 * [40])

    def test_hourly_caffeine_for_user_overall(self):
        user = User.objects.create(username='testuser', token='foo')
        drinks, maxval = self._create_random_caffeine(
            users=[user], number=100, timespan=timedelta(days=365))
        hourly_caffeine = Caffeine.objects.hourly_caffeine_for_user_overall(
            user=user)
        self.assertEqual(hourly_caffeine['maxvalue'], maxval['hour'])
        self.assertEqual(hourly_caffeine['labels'],
                         [unicode(hour) for hour in range(24)])
        self.assertEqual(hourly_caffeine['coffee'],
                         drinks[DRINK_TYPES.coffee]['hour'])
        self.assertEqual(hourly_caffeine['mate'],
                         drinks[DRINK_TYPES.mate]['hour'])

    def test_hourly_caffeine_overall(self):
        users = self._create_users(10)
        drinks, maxval = self._create_random_caffeine(
            users=users, number=100, timespan=timedelta(days=365))
        hourly_caffeine = Caffeine.objects.hourly_caffeine_overall()
        self.assertEqual(hourly_caffeine['maxvalue'], maxval['hour'])
        self.assertEqual(hourly_caffeine['labels'],
                         [unicode(hour) for hour in range(24)])
        self.assertEqual(hourly_caffeine['coffee'],
                         drinks[DRINK_TYPES.coffee]['hour'])
        self.assertEqual(hourly_caffeine['mate'],
                         drinks[DRINK_TYPES.mate]['hour'])

    def test_weekdaily_caffeine_for_user_overall(self):
        user = User.objects.create(username='testuser', token='foo')
        drinks, maxval = self._create_random_caffeine(
            users=[user], number=50, timespan=timedelta(days=30))
        weekdaily_caffeine = \
            Caffeine.objects.weekdaily_caffeine_for_user_overall(
                user=user
            )
        self.assertEqual(weekdaily_caffeine['maxvalue'], maxval['wday'])
        self.assertEqual(weekdaily_caffeine['labels'], WEEKDAY_LABELS)
        self.assertEqual(weekdaily_caffeine['coffee'],
                         drinks[DRINK_TYPES.coffee]['wday'])
        self.assertEqual(weekdaily_caffeine['mate'],
                         drinks[DRINK_TYPES.mate]['wday'])

    def test_weekdaily_caffeine_overall(self):
        users = self._create_users(10)
        drinks, maxval = self._create_random_caffeine(
            users=users, number=50, timespan=timedelta(days=30))
        weekdaily_caffeine = Caffeine.objects.weekdaily_caffeine_overall()
        self.assertEqual(weekdaily_caffeine['maxvalue'], maxval['wday'])
        self.assertEqual(weekdaily_caffeine['labels'], WEEKDAY_LABELS)
        self.assertEqual(weekdaily_caffeine['coffee'],
                         drinks[DRINK_TYPES.coffee]['wday'])
        self.assertEqual(weekdaily_caffeine['mate'],
                         drinks[DRINK_TYPES.mate]['wday'])

    def test_find_recent_caffeine_no_caffeine(self):
        user = User.objects.create(username='testuser', token='foo')
        Caffeine.objects.create(user=user, ctype=DRINK_TYPES.coffee,
                                date=timezone.now() - timedelta(days=2))
        Caffeine.objects.create(user=user, ctype=DRINK_TYPES.mate,
                                date=timezone.now())
        self.assertFalse(
            Caffeine.objects.find_recent_caffeine(
                user=user, date=timezone.now(), ctype=DRINK_TYPES.coffee)
        )

    def test_find_recent_caffeine_caffeine(self):
        user = User.objects.create(username='testuser', token='foo')
        Caffeine.objects.create(user=user, ctype=DRINK_TYPES.coffee,
                                date=timezone.now() - timedelta(days=2))
        latest = Caffeine.objects.create(
            user=user, ctype=DRINK_TYPES.coffee,
            date=timezone.now() - timedelta(seconds=60))
        self.assertEqual(
            Caffeine.objects.find_recent_caffeine(
                user=user, date=timezone.now(), ctype=DRINK_TYPES.coffee),
            latest
        )

    def test_latest_caffeine_activity(self):
        users = self._create_users(5)
        now = timezone.now()
        drinks = [
            Caffeine.objects.create(
                user=random.choice(users),
                ctype=random.choice(list(DRINK_TYPES))[0],
                date=now - timedelta(seconds=random.randrange(86400))
            )
            for _ in range(20)
        ]
        ref = [
            drink.id for drink in
            sorted(drinks, key=lambda x: x.date, reverse=True)[:-10]
        ]
        self.assertEqual(
            [drink.id for drink in
             Caffeine.objects.latest_caffeine_activity()],
            ref)

    def test_top_consumers_total(self):
        users = self._create_users(20)
        matecount = 1
        coffeecount = 20
        now = timezone.now()
        for user in users:
            for _ in range(coffeecount):
                Caffeine.objects.create(
                    user=user, ctype=DRINK_TYPES.coffee,
                    date=now - timedelta(
                        days=random.randrange(100),
                        seconds=random.randrange(86400)))
            coffeecount -= 1
            for _ in range(matecount):
                Caffeine.objects.create(
                    user=user, ctype=DRINK_TYPES.mate,
                    date=now - timedelta(
                        days=random.randrange(100),
                        seconds=random.randrange(86400)))
            matecount += 1
        toptotal = Caffeine.objects.top_consumers_total(DRINK_TYPES.coffee)
        self.assertEqual([item['user'] for item in toptotal],
                         users[:10])
        self.assertEqual([item['caffeine_count'] for item in toptotal],
                         range(20, 10, -1))
        toptotal = Caffeine.objects.top_consumers_total(DRINK_TYPES.mate)
        self.assertEqual([item['user'] for item in toptotal],
                         list(reversed(users[-10:])))
        self.assertEqual([item['caffeine_count'] for item in toptotal],
                         range(20, 10, -1))

    def test_top_consumers_average(self):
        users = self._create_users(20)
        matecount = 2
        coffeecount = 21
        now = timezone.now()
        td = timedelta(days=30)
        for user in users:
            for num in range(coffeecount):
                Caffeine.objects.create(
                    user=user, ctype=DRINK_TYPES.coffee,
                    date=now - (num * td / coffeecount))
            coffeecount -= 1
            for num in range(matecount):
                Caffeine.objects.create(
                    user=user, ctype=DRINK_TYPES.mate,
                    date=now - (num * td / matecount))
            matecount += 1
        topavg = Caffeine.objects.top_consumers_average(DRINK_TYPES.coffee)
        self.assertEqual([item['user'] for item in topavg],
                         users[:10])
        averages = [item['average'] for item in topavg]
        self.assertTrue(averages, sorted(averages, reverse=True))
        topavg = Caffeine.objects.top_consumers_average(DRINK_TYPES.mate)
        self.assertEqual([item['user'] for item in topavg],
                         list(reversed(users[-10:])))
        averages = [item['average'] for item in topavg]
        self.assertTrue(averages, sorted(averages, reverse=True))

    def test_get_csv_data(self):
        user = User.objects.create()
        td = timedelta(days=1)
        now = timezone.now()
        coffees = sorted([
            Caffeine.objects.create(
                user=user, ctype=DRINK_TYPES.coffee,
                date=now - 30 * td / (random.randrange(30) + 1))
            for _ in range(20)
        ], key=lambda x: x.date)
        mate = sorted([
            Caffeine.objects.create(
                user=user, ctype=DRINK_TYPES.mate,
                date=now - 30 * td / (random.randrange(30) + 1))
            for _ in range(20)
        ], key=lambda x: x.date)
        csvdata = Caffeine.objects.get_csv_data(DRINK_TYPES.coffee, user)
        lines = csvdata.split("\r\n")
        self.assertEqual(lines[0], 'Timestamp')
        self.assertEqual(lines[1:-1], [
            coffee.date.strftime(settings.CAFFEINE_DATETIME_FORMAT)
            for coffee in coffees])
        self.assertEqual(lines[-1], '')
        csvdata = Caffeine.objects.get_csv_data(DRINK_TYPES.mate, user)
        lines = csvdata.split("\r\n")
        self.assertEqual(lines[0], 'Timestamp')
        self.assertEqual(lines[1:-1], [
            mateitem.date.strftime(settings.CAFFEINE_DATETIME_FORMAT)
            for mateitem in mate])
        self.assertEqual(lines[-1], '')


class CaffeineTest(TestCase):

    def test_manager_is_caffeinemanager(self):
        self.assertIsInstance(Caffeine.objects, CaffeineManager)

    def test___unicode___without_timezone(self):
        user = User.objects.create(username='testuser')
        caff = Caffeine.objects.create(ctype=DRINK_TYPES.coffee,
                                       date=timezone.now(),
                                       user=user)
        self.assertRegexpMatches(
            unicode(caff),
            r'^%s at \d{4}-\d{2}-\d{2} [^ ]+$' % (
                DRINK_TYPES[DRINK_TYPES.coffee],)
        )

    def test___unicode___with_timezone(self):
        user = User.objects.create(username='testuser')
        caff = Caffeine.objects.create(ctype=DRINK_TYPES.mate,
                                       date=timezone.now(),
                                       user=user, timezone='GMT')
        self.assertRegexpMatches(
            unicode(caff),
            r'^%s at \d{4}-\d{2}-\d{2} [^ ]+ GMT$' % (
                DRINK_TYPES[DRINK_TYPES.mate],)
        )

    def test_format_type(self):
        user = User.objects.create(username='testuser')
        caff = Caffeine.objects.create(ctype=DRINK_TYPES.coffee,
                                       date=timezone.now(),
                                       user=user)
        self.assertEqual(caff.format_type(),
                         DRINK_TYPES[DRINK_TYPES.coffee])


class ActionManagerTest(TestCase):

    def test_create_action(self):
        user = User.objects.create(username='testuser')
        for actiontype in list(ACTION_TYPES):
            action = Action.objects.create_action(
                user, actiontype[0], 'test', 10)
            self.assertEqual(len(action.code), 32)
            self.assertLessEqual(
                action.validuntil,
                timezone.now() + timedelta(10))


class ActionTest(TestCase):

    def test_manager_is_actionmanager(self):
        self.assertIsInstance(Action.objects, ActionManager)

    def test___unicode__(self):
        action = Action.objects.create_action(
            User.objects.create(username='testuser'),
            ACTION_TYPES.change_email, 'test', 10)
        self.assertRegexpMatches(
            unicode(action),
            r'^%s valid until \d{4}-\d{2}-\d{2} [0-9:.]+$' % (
                ACTION_TYPES[ACTION_TYPES.change_email]))
