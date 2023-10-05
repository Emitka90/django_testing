from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.notes = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='tester',
            author=cls.author,
        )

    def test_pages_availability(self):
        ''' Проверка доступности страниц '''
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_anonimous_client(self):
        ''' Проверка страниц недоступных анонимному пользователю '''
        urls = (
            ('notes:add', None),
            ('notes:list', None),
            ('notes:success', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertNotEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_client(self):
        ''' Проверка доступности страниц авторизованному пользоателю '''
        urls = (
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
        )
        self.client.force_login(self.reader)
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_note_edit_detail_delete(self):
        ''' Теструем страницы доступные только автору '''
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in (
                'notes:edit', 'notes:delete', 'notes:detail'
            ):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.notes.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        ''' Тестрование редиректов анонимного пользователя '''
        login_url = reverse('users:login')
        for name, args in (
            ('notes:add', None),
            ('notes:list', None),
            ('notes:success', None),
            ('notes:edit', (self.notes.slug,)),
            ('notes:detail', (self.notes.slug,)),
            ('notes:delete', (self.notes.slug,)),
        ):
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
