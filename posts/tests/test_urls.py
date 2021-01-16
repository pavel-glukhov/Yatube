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
        cls.user_01 = get_user_model().objects.create(
            username=cls.AUTH_USER_NAME_AUTHOR)
        # простой пользователь
        cls.user_02 = get_user_model().objects.create(
            username=cls.AUTH_USER_NAME_GUEST)

        cls.group = Group.objects.create(title='Тестовая группа',
                                         slug='test-group',
                                         description='test-group-description')
        cls.post = Post.objects.create(text='Тестовое сообщение',
                                       author=cls.user_01,
                                       group=cls.group)

    def setUp(self):
        # создадим гостевого пользователя
        self.guest_client = Client()
        # создадим двух авторизованных  пользователей
        self.authorized_client_00 = Client()
        self.authorized_client_00.force_login(self.user_01)

        self.authorized_client_01 = Client()
        self.authorized_client_01.force_login(self.user_02)

        # Словари для проверки доступности страниц и шаблонов"
        # объявим reverse_name для страниц, дабы уменьшить дублирование кода
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
                'post_id': 1
            }
        )

        self.reverse_name_post_edit = reverse(
            'post_edit', kwargs={
                'username': self.AUTH_USER_NAME_AUTHOR,
                'post_id': 1
            }
        )

        self.templates_url_names = {
            'index.html': self.reverse_name_index,
            'posts/group.html': self.reverse_name_group,
            'posts/profile.html': self.reverse_name_profile,
            'posts/post_new_edit.html': self.reverse_name_post_edit
        }

        # Словарь для проверки доступности страниц для автор-ных пользователей
        # Будем проверять:
        # Index - главная страница
        # group_post - страница группы
        # new_post - страница создания новых постов
        # profile - страница профиля с пользователями
        # post - страница с одним постом
        # post_edit - редактирование поста
        # Тестирование осуществляется от лица владельца созданного поста

        self.auth_users_resp_st_code = {
            self.reverse_name_index: 200,
            self.reverse_name_group: 200,
            self.reverse_name_new_post: 200,
            self.reverse_name_profile: 200,
            self.reverse_name_post: 200,
            self.reverse_name_post_edit: 200,
        }

    def test_url_new_post_guest_users(self):
        """Тестирование URL-New_Post для неавторизованных пользователей."""
        # Удостоверися, что редирект на sign up работает корректно
        response = self.guest_client.get(self.reverse_name_new_post,
                                         follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/new/')

    """Проверим страницу редактирования постов
        Необходимо убедиться, что доступ имеется только у автора поста.
        Гость должен быть перенаправлен на страницу авторизации, 
        а авторизованный пользователь не являющийся владельцем, получит 403"""

    def test_url_edit_post_guest_users(self):
        """Тестирование URL: Edit Post для гостей"""
        # Удостоверися, что редирект на sign up работает корректно
        response = self.guest_client.get(self.reverse_name_post_edit)
        self.assertRedirects(
            response, f'/auth/login/?next=/{self.AUTH_USER_NAME_AUTHOR}/'
                      f'{self.post.pk}/edit/'
        )

    def test_url_edit_post_not_owner(self):
        """Тестирование URL: Edit Post для авторизованного невладельца поста"""
        response = self.authorized_client_01.get(self.reverse_name_post_edit)
        self.assertRedirects(
            response, f'/{self.AUTH_USER_NAME_AUTHOR}/{self.post.pk}/')

    def test_urls_authorized_users(self):
        """Тестирование URL для авторизованных пользователей."""
        for reverse_name, status_code in self.auth_users_resp_st_code.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client_00.get(reverse_name)
                self.assertEqual(status_code, response.status_code,
                                 f'Неправильная работа reverse name:'
                                 f' {reverse_name} для неавторизованного '
                                 f'пользователя. Код: {status_code}')

    def test_url_correct_templates(self):
        """Тестирование доступности шаблонов по reverse name"""

        for template, reverse_name in self.templates_url_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client_00.get(reverse_name)
                self.assertTemplateUsed(response, template,
                                        f'Проблема с шаблоном: {template}'
                                        f' reverse name: {reverse_name} ')
