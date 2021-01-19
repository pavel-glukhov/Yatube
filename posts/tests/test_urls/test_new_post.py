from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post


class EditURLTests(TestCase):
    AUTH_USER_NAME_AUTHOR = 'TestUser1'
    AUTH_USER_NAME_GUEST = 'TestUser2'

    def setUp(self):
        # автор поста
        self.auth_post_author = get_user_model().objects.create(
            username=self.AUTH_USER_NAME_AUTHOR)
        # пользователь читатель
        self.auth_post_reader = get_user_model().objects.create(
            username=self.AUTH_USER_NAME_GUEST)

        self.group = Group.objects.create(title='Тестовая группа',
                                          slug='test-group',
                                          description='test-group-description'
                                          )
        self.post = Post.objects.create(text='Тестовое сообщение',
                                        author=self.auth_post_author,
                                        group=self.group
                                        )
        # создадим гостевого пользователя
        self.guest_client = Client()

        self.reverse_name_new_post = reverse('new_post')

    def test_url_new_post_guest_users(self):
        """Тестирование URL-New_Post для неавторизованных пользователей."""
        # Удостоверися, что редирект на sign up работает корректно
        # и гости не смогу получить доступ к новым постам

        response = self.guest_client.get(self.reverse_name_new_post,
                                         follow=True
                                         )
        self.assertRedirects(
            response, '/auth/login/?next=/new/')
