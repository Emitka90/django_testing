from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from news.forms import BAD_WORDS
from news.models import Comment, News

today = datetime.today()
now = timezone.now()


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст новости',
    )
    return news


@pytest.fixture
def news_more():
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 5)
    ]
    return News.objects.bulk_create(all_news)


@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(
        text='Текст новости',
        news=news,
        author=author
    )
    return comment


@pytest.fixture
def comments_more(comment, news, author):
    for index in range(2):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()
        return comment


@pytest.fixture
def id_for_news_args(news):
    return news.id,


@pytest.fixture
def id_for_comment_args(comment):
    return comment.id,


@pytest.fixture
def form_data():
    return {
        'text': 'Новый комментарий',
    }


@pytest.fixture
def bad_words_data():
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    return bad_words_data


@pytest.fixture
def news_detail_url(news):
    return reverse('news:detail', args=(news.id,))
