from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post
from django.core.cache import cache


class ContextPageViewTests(TestCase):
    AUTH_USER_NAME = 'TestUser'
    PAGE_TEXT = 'Тестовое сообщение1'
    PAGE_GROUP = 'Тестовая группа'
    GROUP_SLUG = 'test-group'
    GROUP_DESCR = 'Описание группы'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = get_user_model().objects.create(
            username=cls.AUTH_USER_NAME
        )
        Group.objects.create(title=cls.PAGE_GROUP,
                             slug=cls.GROUP_SLUG,
                             description=cls.GROUP_DESCR
                             )

        cls.post = Post.objects.create(
            text=cls.PAGE_TEXT,
            author=cls.user,
            group=Group.objects.get(slug=cls.GROUP_SLUG)
        )

    def setUp(self):
        self.guest_user = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_context_in_new_post_page(self):
        """ Тестирование содержания context в new_post"""
        cache.clear()
        response = self.authorized_client.get(reverse('new_post'))

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            form_field = response.context.get('form').fields.get(value)
            self.assertIsInstance(form_field, expected,
                                  'Данные переданные в context из формы,'
                                  'не соответствуют записям')

    def test_context_in_index_page(self):
        """ Тестирование содержания context в index"""
        cache.clear()
        response = self.authorized_client.get(reverse('index'))

        context_post = {
            self.PAGE_TEXT: response.context['page'][0].text,
            self.AUTH_USER_NAME: response.context['page'][0].author.username,
            self.PAGE_GROUP: response.context['page'][0].group.title
        }

        for expected, value in context_post.items():
            with self.subTest():
                self.assertEqual(value, expected,
                                 'Данные переданные в context'
                                 'не соответствуют записям')

    def test_context_in_group_page(self):
        """ Тестирование содержания context в group"""
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': self.GROUP_SLUG}))

        # group передает словарь с двумя ключами posts и group,
        # проверим их содержание

        context_group = {
            self.PAGE_TEXT: response.context['page'][0].text,
            self.AUTH_USER_NAME: response.context['page'][0].author.username,
            self.PAGE_GROUP: response.context['group'].title,
            self.GROUP_SLUG: response.context['group'].slug,
            self.GROUP_DESCR: response.context['group'].description
        }

        for expected, value in context_group.items():
            with self.subTest():
                self.assertEqual(value, expected, 'Данные переданные'
                                                  ' в context не'
                                                  ' соответствуют'
                                                  ' записям')

    def test_context_in_edit_post_page(self):
        """Тестирование содержания context при редактировании поста"""

        response = self.authorized_client.get(
            reverse('post_edit',
                    kwargs={'username': self.AUTH_USER_NAME,
                            'post_id': self.post.id
                            }))

        context_edit_page = {
            self.PAGE_TEXT: response.context.get('post').text,
            self.PAGE_GROUP: response.context.get('post').group.title,
        }

        for expected, value in context_edit_page.items():
            with self.subTest():
                self.assertEqual(value, expected, 'Данные переданные'
                                                  ' в context не'
                                                  ' соответствуют'
                                                  ' записям'
                                 )

    def test_context_in_profile_page(self):
        """Тестирование содержания context для profile"""

        response = self.guest_user.get(
            reverse('profile',
                    kwargs={'username': self.AUTH_USER_NAME}))

        context_edit_page = {
            self.PAGE_TEXT: response.context['page'][0].text,
            self.PAGE_GROUP: response.context['page'][0].group.title,
            self.AUTH_USER_NAME: response.context['page'][0].author.username,
        }

        for expected, value in context_edit_page.items():
            with self.subTest():
                self.assertEqual(value, expected, 'Данные переданные'
                                                  ' в context не'
                                                  ' соответствуют'
                                                  ' записям'
                                 )

    def test_context_in_post_id_page(self):
        """Тестирование context для страницы индивидуального поста"""

        response = self.guest_user.get(
            reverse('post',
                    kwargs={
                        'username': self.AUTH_USER_NAME,
                        'post_id': self.post.id
                    }))

        context_edit_page = {
            self.PAGE_TEXT: response.context.get('post').text,
            self.PAGE_GROUP: response.context.get('post').group.title,
            self.AUTH_USER_NAME: response.context.get('post').author.username,
        }

        for expected, value in context_edit_page.items():
            with self.subTest():
                self.assertEqual(value, expected, 'Данные переданные'
                                                  ' в context не'
                                                  ' соответствуют'
                                                  ' записям'
                                 )
