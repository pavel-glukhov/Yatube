from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post


class TemplateViewTests(TestCase):
    AUTH_USER_NAME = 'TestUser'
    PAGE_TEXT = 'Тестовое сообщение1'
    PAGE_GROUP = 'Тестовая группа'
    GROUP_SLUG = 'test-group'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = get_user_model().objects.create(
            username=cls.AUTH_USER_NAME)

        Group.objects.create(title=cls.PAGE_GROUP,
                             slug=cls.GROUP_SLUG,
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

    def test_templates_via_reverse_name(self):
        """Тестирование шаблонов HTML"""
        # Удостоверимся, что страницы используют ожидаемые шаблоны HTML

        templates_url_names = {
            'index.html': reverse('index'),
            'posts/group.html': reverse('group',
                                        kwargs={'slug': self.GROUP_SLUG}),
            'posts/post_new_edit.html': reverse('new_post'),
        }

        for template, reverse_name in templates_url_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template,
                                        f'Проблема с шаблоном: {template}'
                                        f' reverse name: {reverse_name} '
                                        )
