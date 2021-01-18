from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post


class PostURLTests(TestCase):
    AUTH_USER_NAME_AUTHOR = 'TestUser1'
    AUTH_USER_NAME_GUEST = 'TestUser2'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # создадим двух пользователей в базе данных
        # Автор поста
        cls.user_guest = get_user_model().objects.create(
            username=cls.AUTH_USER_NAME_AUTHOR)

        cls.user_author = get_user_model().objects.create(
            username=cls.AUTH_USER_NAME_GUEST)

        cls.group = Group.objects.create(title='Тестовая группа',
                                         slug='test-group',
                                         description='test-group-description'
                                         )
        cls.post = Post.objects.create(text='Тестовое сообщение',
                                       author=cls.user_author,
                                       group=cls.group
                                       )

    def setUp(self):
        # создадим гостевого пользователя
        self.guest_client = Client()

        self.reverse_name_comment = reverse(
            'add_comment', kwargs={
                'username': self.AUTH_USER_NAME_AUTHOR,
                'post_id': self.post.pk
            }
        )

    def test_url_comment_post_guest_users(self):
        """Тестирование URL: Comment для гостей сайта"""
        # Удостоверися, что редирект на sign up работает корректно и comment
        # не будут доступен для неавторизованных пользователей
        response = self.guest_client.get(self.reverse_name_comment)
        self.assertRedirects(
            response, f'/auth/login/?next=/{self.AUTH_USER_NAME_AUTHOR}/'
                      f'{self.post.pk}/comment'
        )
