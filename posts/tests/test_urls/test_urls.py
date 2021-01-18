from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post


class PostURLTests(TestCase):

    AUTH_USER_NAME_AUTHOR = 'TestUser1'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Автор поста
        cls.user_author = get_user_model().objects.create(
            username=cls.AUTH_USER_NAME_AUTHOR)

        cls.group = Group.objects.create(title='Тестовая группа',
                                         slug='test-group',
                                         description='test-group-description'
                                         )
        cls.post = Post.objects.create(text='Тестовое сообщение',
                                       author=cls.user_author,
                                       group=cls.group
                                       )

    def setUp(self):
        # создадим авторизованного пользователя
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_author)

        self.reverse_name_index = reverse('index')
        self.reverse_name_new_post = reverse('new_post')
        self.reverse_name_group = reverse('group',
                                          kwargs={'slug': 'test-group'})
        self.reverse_name_profile = reverse(
            'profile', kwargs={'username': self.AUTH_USER_NAME_AUTHOR}
        )
        self.reverse_name_post = reverse(
            'post', kwargs={
                'username': self.AUTH_USER_NAME_AUTHOR,
                'post_id': self.post.pk
            }
        )

        self.reverse_name_post_edit = reverse(
            'post_edit', kwargs={
                'username': self.AUTH_USER_NAME_AUTHOR,
                'post_id': self.post.pk
            }
        )

        self.reverse_name_comment = reverse(
            'add_comment', kwargs={
                'username': self.AUTH_USER_NAME_AUTHOR,
                'post_id': self.post.pk
            }
        )

        self.auth_users_resp_st_code = {
            self.reverse_name_index: 200,
            self.reverse_name_group: 200,
            self.reverse_name_new_post: 200,
            self.reverse_name_profile: 200,
            self.reverse_name_post: 200,
            self.reverse_name_post_edit: 200,
            self.reverse_name_comment: 200,

        }

    def test_urls_authorized_users(self):
        """Тестирование URL для авторизованных пользователей."""
        for reverse_name, status_code in self.auth_users_resp_st_code.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(status_code, response.status_code,
                                 f'Неправильная работа reverse name:'
                                 f' {reverse_name} для неавторизованного '
                                 f'пользователя. Код: {status_code}'
                                 )
