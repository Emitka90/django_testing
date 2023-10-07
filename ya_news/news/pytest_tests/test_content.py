import pytest

from django.conf import settings
from django.urls import reverse


@pytest.mark.django_db
def test_news_count(client, news_more):
    ''' Проверяем количество выводимых новостей '''
    url = reverse('news:home')
    response = client.get(url, context=news_more)
    object_list = response.context['object_list']
    assert len(object_list) == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, news_more):
    ''' Проверяем сортировку новостей по дате '''
    url = reverse('news:home')
    response = client.get(url, context=news_more)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert sorted_dates == all_dates


@pytest.mark.django_db
def test_comments_order(client, news_detail_url, comments_more):
    ''' Проверяем сортировку комментариев '''
    response = client.get(news_detail_url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    assert all_comments[0].created < all_comments[1].created


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, form_in_list',
    (
        (pytest.lazy_fixture('client'), False),
        (pytest.lazy_fixture('admin_client'), True),
    )
)
def test_create_news_page_comment_form(
    parametrized_client, form_in_list, news_detail_url
):
    '''
    Проверяем наличие формы в контексте для авторизованного
    и неавторизованного пользователя
    '''
    response = parametrized_client.get(news_detail_url)
    assert ('form' in response.context) is form_in_list


@pytest.mark.django_db
def test_edit_note_page_contains_form(id_for_comment_args, author_client):
    ''' Проверяем наличие формы редактирования комментария '''
    url = reverse('news:edit', args=id_for_comment_args)
    response = author_client.get(url)
    assert 'form' in response.context
