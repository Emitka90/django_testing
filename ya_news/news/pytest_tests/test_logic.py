from http import HTTPStatus

import pytest

from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import WARNING
from news.models import Comment


def test_user_can_create_comment(
        admin_client, form_data, news_detail_url, comment_initial_count
):
    ''' Тестируем возможность пользователем оставить комментарий '''
    response = admin_client.post(news_detail_url, data=form_data)
    assertRedirects(response, f'{news_detail_url}#comments')
    assert Comment.objects.count() == comment_initial_count + 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']


@pytest.mark.django_db
def test_anonymous_user_cant_create_note(
    client, form_data, news_detail_url, comment_initial_count
):
    '''
    Тестируем невозможность анонимным пользователем оставить комментарий
    '''
    response = client.post(news_detail_url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={news_detail_url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == comment_initial_count


def test_user_cant_use_bad_words(
        admin_client, bad_words_data, news_detail_url, comment_initial_count
):
    ''' Проверка блокировки стоп-слов '''
    response = admin_client.post(news_detail_url, data=bad_words_data)
    assertFormError(response, 'form', 'text', errors=WARNING)
    assert Comment.objects.count() == comment_initial_count


@pytest.mark.django_db
def test_author_can_edit_comment(
        comment, author_client, form_data, news_detail_url
):
    ''' Проверяем, что автор может изменить свой комментарий '''
    url = reverse('news:edit', args=(comment.id,))
    response = author_client.post(url, form_data)
    assertRedirects(response, f'{news_detail_url}#comments')
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_user_cant_edit_comment_of_another_user(
        admin_client, form_data, comment
):
    ''' Проверяем, что пользователь не может изменить чужой комментарий '''
    url = reverse('news:edit', args=(comment.id,))
    response = admin_client.post(url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text


def test_author_can_delete_comment(
    author_client, id_for_comment_args, news_detail_url, comment_initial_count
):
    ''' Проверяем, что автор может удалить свой комментарий '''
    print(comment_initial_count)
    url = reverse('news:delete', args=id_for_comment_args)
    response = author_client.post(url)
    assertRedirects(response, f'{news_detail_url}#comments')
    assert Comment.objects.count() < comment_initial_count


def test_user_cant_delete_comment_of_another_user(
        admin_client, id_for_comment_args, comment_initial_count
):
    ''' Проверяем, что пользователь не может удалить чужой комментарий '''
    url = reverse('news:delete', args=id_for_comment_args)
    response = admin_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == comment_initial_count
