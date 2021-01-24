from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post
from django.core.cache import cache


class TemplatesURLTests(TestCase):
    AUTH_USER_NAME_AUTHOR = 'TestUser1'
    AUTH_USER_NAME_GUEST = 'TestUser2'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = get_user_model().objects.create(
            username=cls.AUTH_USER_NAME_AUTHOR)

        cls.group = Group.objects.create(title='Тестовая группа',
                                         slug='test-group',
                                         description='test-group-description'
                                         )
        cls.post = Post.objects.create(text='Тестовое сообщение',
                                       author=cls.user,
                                       group=cls.group
                                       )

    def setUp(self):

        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        # объявим reverse_name для страниц
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

        self.reverse_name_comment = reverse(
            'add_comment', kwargs={
                'username': self.AUTH_USER_NAME_AUTHOR,
                'post_id': self.post.pk
            }
        )

        # словать шаблонов
        self.templates_url_names = {
            'index.html': self.reverse_name_index,
            'posts/group.html': self.reverse_name_group,
            'posts/post.html': self.reverse_name_post,
            'posts/profile.html': self.reverse_name_profile,
            'posts/post_new_edit.html': self.reverse_name_new_post,
            'posts/comments.html': self.reverse_name_comment,
        }

    def test_url_correct_templates(self):
        """Тестирование доступности шаблонов по reverse name"""
        for template, reverse_name in self.templates_url_names.items():
            with self.subTest(reverse_name=reverse_name):
                cache.clear()
                response = self.authorized_client.get(reverse_name)

                self.assertTemplateUsed(response, template,
                                        f'Проблема с шаблоном: {template}'
                                        f' reverse name: {reverse_name} '
                                        )
