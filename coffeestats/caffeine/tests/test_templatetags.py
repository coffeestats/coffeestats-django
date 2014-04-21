from django.core.urlresolvers import reverse
from django.http import HttpRequest
from django.test import TestCase
from django.contrib.auth import get_user_model

import caffeine.templatetags.caffeine as tags


User = get_user_model()


class RequestTagTestMixin(object):

    def _create_request(self):
        request = HttpRequest()
        request.META.update({
            'SERVER_NAME': 'localhost',
            'SERVER_PORT': 8000,
        })
        return request


class PublicUrlTest(RequestTagTestMixin, TestCase):

    def test_no_user(self):
        with self.assertRaises(KeyError):
            tags.publicurl({})

    def test_profileuser_without_request(self):
        testuser = User.objects.create(username='testuser')
        with self.assertRaises(KeyError):
            tags.publicurl({'profileuser': testuser})

    def test_profileuser_with_request(self):
        testuser = User.objects.create(username='testuser')
        url = tags.publicurl({'request': self._create_request(),
                              'profileuser': testuser})
        self.assertTrue(url.endswith(reverse(
            'public', kwargs={'username': 'testuser'})))

    def test_with_username(self):
        url = tags.publicurl({'request': self._create_request()},
                             username='testuser')
        self.assertTrue(url.endswith(reverse(
            'public', kwargs={'username': 'testuser'})))


class OnTheRunUrlTest(RequestTagTestMixin, TestCase):

    def test_no_user(self):
        with self.assertRaises(KeyError):
            tags.ontherunurl({})

    def test_profileuser_without_request(self):
        testuser = User.objects.create(username='testuser')
        with self.assertRaises(KeyError):
            tags.ontherunurl({'profileuser': testuser})

    def test_profileuser_with_request(self):
        testuser = User.objects.create(username='testuser', token='bla')
        url = tags.ontherunurl({'request': self._create_request(),
                                'profileuser': testuser})
        self.assertTrue(url.endswith(reverse(
            'ontherun', kwargs={'username': 'testuser', 'token': 'bla'})))

    def test_with_user(self):
        testuser = User.objects.create(username='testuser', token='bla')
        url = tags.ontherunurl({'request': self._create_request()},
                               user=testuser)
        self.assertTrue(url.endswith(reverse(
            'ontherun', kwargs={'username': 'testuser', 'token': 'bla'})))


class MessagetagsTest(TestCase):

    class _message(object):

        def __init__(self, text, tags):
            self.text = text
            self.tags = tags

    def test_empty_messages(self):
        self.assertEqual(tags.messagetags([], None), [])

    def test_empty_for_non_matching_tags(self):
        message1 = MessagetagsTest._message('test', ['notinteresting'])

        self.assertEqual(tags.messagetags([message1], 'interesting'),
                         [])

    def test_matching_tags_only(self):
        message1 = MessagetagsTest._message('test1', ['notinteresting'])
        message2 = MessagetagsTest._message('test2', ['interesting'])
        message3 = MessagetagsTest._message('test3', ['interesting', 'error'])

        self.assertEqual(tags.messagetags(
            [message1, message2, message3], 'interesting'),
            [message2, message3])
