from django.test import Client, TestCase
from django.urls import reverse


class StaticViewsTests(TestCase):

    def setUp(self):
        self.guest_user = Client()
        self.templates_url_names = {
            'about/author.html': reverse('about:author'),
            'about/tech.html': reverse('about:tech'),
        }

    def test_templates_static_pages(self):
        """Тестирование шаблонов для статических страниц """
        for template, reverse_name in self.templates_url_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_user.get(reverse_name)
                self.assertTemplateUsed(response, template,
                                        f'Проблема с шаблоном: {template}'
                                        f' reverse name: {reverse_name} ')
