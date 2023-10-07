from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestContent(TestCase):
    NOTES_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        all_notes = [
            Note(
                title='Новость',
                text='Просто текст.',
                author=cls.author,
                slug=f'aba{index}'
            )
            for index in range(1, 11)
        ]
        Note.objects.bulk_create(all_notes)
        cls.note_obj = Note.objects.get(pk=1)

    def test_notes_order(self):
        ''' Тестируем сортировку заметок '''
        self.client.force_login(self.author)
        response = self.client.get(self.NOTES_URL)
        notes_list = response.context['object_list']
        all_id = [note.pk for note in notes_list]
        sorted_id = sorted(all_id)
        self.assertEqual(all_id, sorted_id)

    def test_note_not_in_list_for_author(self):
        '''
        Проверяем, что со списком заметок, в списке object_list,
        передаются заметки пользователя
        '''
        self.client.force_login(self.author)
        response = self.client.get(self.NOTES_URL)
        object_list = response.context['object_list']
        self.assertIn(self.note_obj, object_list)

    def test_note_not_in_list_for_another_user(self):
        '''
        Проверяем, что со списком заметок, в списке object_list,
        не попадают заметки другого пользователя
        '''
        self.client.force_login(self.reader)
        response = self.client.get(self.NOTES_URL)
        object_list = response.context['object_list']
        self.assertNotIn(self.note_obj, object_list)


class TestDetailPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.notes = Note.objects.create(
            title='Заметка',
            text='Просто текст.',
            author=cls.author,
            slug='tester',
        )
        cls.add_url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=(cls.notes.slug,))

    def test_authorized_client_has_form(self):
        ''' Проверяем наличие формы в контексте '''
        self.client.force_login(self.author)
        for name, args in (
            ('notes:add', None),
            ('notes:edit', (self.notes.slug,)),
        ):
            with self.subTest(user=self.author, name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertIn('form', response.context)
