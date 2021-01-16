from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post


class NewPost_FormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = get_user_model().objects.create(username='TestUser')
        cls.group = Group.objects.create(title='Тестовая группа',
                                         slug='test-group',
                                         description='Описание')
        # создаем авторизованного пользователя
        cls.authorized_user = Client()
        cls.authorized_user.force_login(cls.user)

    def test_forms_new_post(self):
        """Тестируем форму новых сообщений на странице New_Post"""
        # данные для создания нового поста
        form_data = {
            'text': 'Здесь что-то написано',
            'group': self.group.id
        }
        response = self.authorized_user.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        # проверяем, правильно ли работает redirect после создания нового поста
        self.assertRedirects(response, reverse('index'))


class PostEdit_FormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = get_user_model().objects.create(username='TestUser')
        cls.group = Group.objects.create(title='Тестовая группа',
                                         slug='test-group',
                                         description='Описание')
        cls.post = Post.objects.create(text='Тестовая запись_фыр_фыр_фыр',
                                       author=cls.user,
                                       group=cls.group)
        # создадим авторизованного пользователя
        cls.authorized_user = Client()
        cls.authorized_user.force_login(cls.user)

        cls.form_data = {
            'text': 'Тестовая запись_быр_быр_быр',
            'group': cls.group.pk,
        }

    def test_forms_post_edit(self):
        """Тестируем форму исправления сообщений на странице New_Post"""

        response = self.authorized_user.post(
            reverse('post_edit',
                    kwargs={'username': 'TestUser',
                            'post_id': self.post.pk}),
            data=self.form_data,
            follow=True)

        self.assertEqual(response.context['post'].text, self.form_data['text'])
