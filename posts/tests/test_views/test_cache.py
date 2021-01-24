from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post


# класс тестирования работоспособности кеширования страниц
class CacheViewTest(TestCase):

    AUTHORIZED_USER_NAME = 'TestUser'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = get_user_model().objects.create(
            username=cls.AUTHORIZED_USER_NAME
        )

        Post.objects.bulk_create([Post(text=f'Test{i}', author=cls.user)
                                  for i in range(5)])
        cls.guest_user = Client()

    def test_index_cache(self):
        """Тестирование работоспособности кеширования на странице Index"""
        cache.clear()
        response = self.guest_user.get(reverse('index'))
        Post.objects.bulk_create([Post(text=f'Test{i}', author=self.user)
                                  for i in range(3)])

        # Вычисление колличества записей context и колличества записей в базе
        context_cache_data_len = len(response.context.get('page').object_list)
        post_context_cache_len = Post.objects.count()

        # длина кеша должна отличаться от колличества записанных постов в базе
        self.assertNotEqual(context_cache_data_len, post_context_cache_len,
                            'Кеширование работает неправильно.'
                            ' Число записей в Context совпадает '
                            'с колличеством записей в базе')
        # очистим кеш и по новой запросим информацию с страницы
        cache.clear()
        response = self.guest_user.get(reverse('index'))
        # вычислим длину
        context_len = len(response.context.get('page').object_list)
        post_len = Post.objects.count()
        # колличество записей должно совпадать
        self.assertEqual(context_len, post_len,
                         'Кеширование работает неверно.'
                         ' Колличество записей после обновления'
                         ' не совпадает')
