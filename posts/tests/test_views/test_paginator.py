from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from posts.models import Post


class PaginatorViewsTest(TestCase):
    """Тестируем Paginator. Страница должна быть разбита на 10 постов"""

    POSTS_COUNT = 13

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = get_user_model().objects.create(username='TestUser')

        Post.objects.bulk_create([Post(
            text=f'Тестовое сообщение{i}',
            author=cls.user)
            for i in range(cls.POSTS_COUNT)])

    def test_first_page_contains_ten_records(self):
        """Тестируем Paginator.Первые 10 постов на первой странице"""

        response = self.client.get(reverse('index'))
        self.assertEqual(
            len(response.context.get('page').object_list),
            settings.POSTS_IN_PAGE
        )

    def test_second_page_contains_three_records(self):
        """Тестируем Paginator.Последние 3 поста на второй странице"""

        response = self.client.get(reverse('index') + '?page=2')
        self.assertEqual(
            len(response.context.get('page').object_list),
            self.POSTS_COUNT - settings.POSTS_IN_PAGE
        )
