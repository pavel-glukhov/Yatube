from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post


class EditURLTests(TestCase):

    AUTH_USER_NAME_AUTHOR = 'TestUser1'
    AUTH_USER_NAME_READER = 'TestUser2'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # создадим двух пользователей в базе данных
        # Автор поста
        cls.auth_post_author = get_user_model().objects.create(
            username=cls.AUTH_USER_NAME_AUTHOR)
        # пользователь читатель
        cls.auth_post_reader = get_user_model().objects.create(
            username=cls.AUTH_USER_NAME_READER)

        cls.group = Group.objects.create(title='Тестовая группа',
                                         slug='test-group',
                                         description='test-group-description'
                                         )
        cls.post = Post.objects.create(text='Тестовое сообщение',
                                       author=cls.auth_post_author,
                                       group=cls.group
                                       )

    def setUp(self):
        # создадим гостевого пользователя
        self.guest_client = Client()
        # создадим двух авторизованных  пользователей
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.auth_post_author)

        self.authorized_client_reader = Client()
        self.authorized_client_reader.force_login(self.auth_post_reader)

        self.reverse_name_post_edit = reverse(
            'post_edit', kwargs={
                'username': self.AUTH_USER_NAME_AUTHOR,
                'post_id': self.post.pk
            }
        )

    def test_url_edit_post_not_owner(self):
        """Тестирование URL: Edit Post для авторизованного невладельца поста"""
        response = self.authorized_client_reader.get(
            self.reverse_name_post_edit
        )
        self.assertRedirects(
            response, f'/{self.AUTH_USER_NAME_AUTHOR}/{self.post.pk}/'
        )

    def test_url_edit_post_guest_users(self):
        """Тестирование URL: Edit Post для гостей"""
        # Удостоверися, что редирект на sign up работает корректно
        response = self.guest_client.get(self.reverse_name_post_edit)
        self.assertRedirects(
            response, f'/auth/login/?next=/{self.AUTH_USER_NAME_AUTHOR}/'
                      f'{self.post.pk}/edit/'
        )
