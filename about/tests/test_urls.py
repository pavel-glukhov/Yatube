from django.test import Client, TestCase
from django.urls import reverse


class StaticURLTests(TestCase):

    def setUp(self):
        self.static_pages = {
            reverse('about:author'): 200,
            reverse('about:tech'): 200,
        }
        self.guest_client = Client()

    def test_urls_static_pages(self):
        """Тестируем статические страницы на доступность"""
        for reverse_name, status_code in self.static_pages.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(status_code, response.status_code,
                                 f'Статическая страница {reverse_name}'
                                 f' недоступна')
