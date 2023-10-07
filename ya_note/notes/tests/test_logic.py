from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note


User = get_user_model()


class TestNoteCreation(TestCase):
    NOTE_TEXT = 'Текст заметки'
    NOTE_SLUG = 'tester'
    NOTE_TITLE = 'Заголовок'

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('notes:add')
        cls.redirect_url = reverse('notes:success')
        cls.user = User.objects.create(username='Человек')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {
            'text': cls.NOTE_TEXT,
            'slug': cls.NOTE_SLUG,
            'title': cls.NOTE_TITLE
        }
        cls.notes_initial_count = Note.objects.all().count()
        cls.id_new_note = cls.notes_initial_count + 1

    def test_anonymous_user_cant_create_note(self):
        ''' Анониманый пользователь не может создать заметку '''
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, self.notes_initial_count)

    def test_user_can_create_note(self):
        ''' Залогиненный пользователь может создать заметку '''
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, f'{self.redirect_url}')
        notes_count = Note.objects.count()
        self.assertGreater(notes_count, self.notes_initial_count)
        note = Note.objects.get(id=self.id_new_note)
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.title, self.NOTE_TITLE)
        self.assertEqual(note.slug, self.NOTE_SLUG)
        self.assertEqual(note.author, self.user)

    def test_unique_slug(self):
        ''' Тестируем уникальность поля slug '''
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, f'{self.redirect_url}')
        notes_first_count = Note.objects.count()
        self.assertGreater(notes_first_count, self.notes_initial_count)
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=self.NOTE_SLUG + WARNING,
        )
        notes_second_count = Note.objects.count()
        self.assertEqual(notes_second_count, notes_first_count)

    def test_not_slug(self):
        ''' Тестируем преобразование title в slug (если не указан slug) '''
        del self.form_data['slug']
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, f'{self.redirect_url}')
        note = Note.objects.get()
        self.assertEqual(note.slug, slugify(self.NOTE_TITLE))


class TestNoteEditDelete(TestCase):
    NOTE_TEXT = 'Текст заметки'
    NEW_NOTE_TEXT = 'Новый текст заметки'
    TITLE = 'Заголовок'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title=cls.TITLE,
            author=cls.author,
            text=cls.NOTE_TEXT
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.redirect_url = reverse('notes:success')
        cls.form_data = {'text': cls.NEW_NOTE_TEXT,
                         'title': cls.TITLE}
        cls.notes_initial_count = Note.objects.all().count()

    def test_author_can_delete_note(self):
        ''' Проверяем, что автор может удалить заметку '''
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, f'{self.redirect_url}')
        notes_count = Note.objects.count()
        self.assertLess(notes_count, self.notes_initial_count)

    def test_user_cant_delete_note_of_another_user(self):
        ''' Проверяем, что пользователь не может удалить чужую заметку. '''
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, self.notes_initial_count)

    def test_author_can_edit_note(self):
        ''' Проверяем, что автор может отредактировать свою заметку '''
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, f'{self.redirect_url}')
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)

    def test_user_cant_edit_note_of_another_user(self):
        ''' Проверяем, что пользователь не может изменить чужую заметку. '''
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)
