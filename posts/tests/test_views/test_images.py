import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post
from django.core.cache import cache


# Класс тестирования постов содержащих в себе изобращение
class PostImageViewTest(TestCase):
    AUTH_USER_NAME = 'TestUser'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

        cls.small_gif = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
                         b'\x01\x00\x80\x00\x00\x00\x00\x00'
                         b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                         b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                         b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                         b'\x0A\x00\x3B'
                         )

        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.user = get_user_model().objects.create(
            username=cls.AUTH_USER_NAME
        )
        cls.group = Group.objects.create(title='Тестовая группа',
                                         slug='test-group'
                                         )
        cls.post = Post.objects.create(text='Тестовая запись',
                                       group=cls.group,
                                       author=cls.user,
                                       image=cls.uploaded
                                       )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_context_index_page(self):
        """Проверяем context страницы index на наличие изображения"""
        cache.clear()
        response = self.guest_client.get(reverse('index'))
        response_data_image = response.context['page'][0].image
        expected = f'posts/{self.uploaded.name}'

        self.assertEqual(response_data_image,
                         expected, 'Изображение переданные'
                                   ' в context страницы index'
                                   ' не соответствует загруженному'
                         )

    def test_context_profile_page(self):
        """Проверяем context страницы profile на наличие изображения"""
        response = self.guest_client.get(
            reverse('profile', kwargs={
                'username': self.AUTH_USER_NAME
            }))

        response_data_image = response.context['page'][0].image
        expected = f'posts/{self.uploaded.name}'

        self.assertEqual(response_data_image,
                         expected, 'Изображение переданные'
                                   ' в context страницы profile'
                                   ' не соответствует загруженному'
                         )

    def test_context_group_page(self):
        """Проверяем context страницы group на наличие изображения"""
        response = self.guest_client.get(reverse('group',
                                                 kwargs={'slug':
                                                         'test-group'
                                                         }))

        response_data_image = response.context['page'][0].image
        expected = f'posts/{self.uploaded.name}'

        self.assertEqual(response_data_image,
                         expected, 'Изображение переданные'
                                   ' в context страницы group'
                                   ' не соответствует загруженному'
                         )

    def test_context_post_page(self):
        """Проверяем context страницы post на наличие изображения"""
        cache.clear()
        response = self.guest_client.get(
            reverse('post', kwargs={'username': self.AUTH_USER_NAME,
                                    'post_id': self.post.pk
                                    }))

        response_data_image = response.context['post'].image
        expected = f'posts/{self.uploaded.name}'

        self.assertEqual(response_data_image,
                         expected, 'Изображение переданное'
                                   ' в context страницы post'
                                   ' не соответствует загруженному'
                         )

    def test_create_post_with_image(self):
        """Проверка создания записи содержащая картинку"""

        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id,
            'image': self.uploaded.name,
        }
        cache.clear()
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        # при успешном создании записи произойдет редирект на гравную страницу
        self.assertRedirects(response, reverse('index'))
