from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post


class PostModelTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = get_user_model().objects.create(username='TestUser',
                                                   first_name='FirstNameUser',
                                                   last_name='LastNameUser')

        cls.group = Group.objects.create(title='Тестовая группа',
                                         slug='test-group',
                                         description='test-group-description')

        cls.post = Post.objects.create(text='Тестовое сообщение',
                                       author=cls.user,
                                       group=cls.group)

    def test_helps_text(self):
        """Тестируем helps_text в модели Post"""
        post = PostModelTest.post
        field_help_text = {
            'text': 'здесь можно писать свою историю',
            'author': 'здесь указан автор поста',
            'group': 'здесь указано сообщество поста'
        }

        for value, expected in field_help_text.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected,
                    (f'Ошибка в {PostModelTest.test_helps_text.__name__},'
                     ' проверьте help_text в Post'))

    def test_verbose_name(self):
        """Тестуруем verbose_name в модели Post"""
        post = PostModelTest.post
        field_verbose_name = {
            'text': 'Текст',
            'pub_date': 'дата публикации',
            'author': 'автор поста',
            'group': 'сообщество'
        }

        for value, expected in field_verbose_name.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected,
                    (f'Ошибка в {PostModelTest.test_verbose_name.__name__},'
                     ' проверьте verbose_name в Post'))

    def test_post_str_value(self):
        """Тестируем длину __str__ значения в модели Post
            метод __str__ должен возвращать строку в 15 символов"""
        self.assertEqual(self.post.__str__(), self.post.text[:15],
                         'Метод __str__ в можели post не'
                         ' возвращает 15 символов поля text')

    def test_group_str_value(self):
        """Тестируем значение __str__  в модели Group
            метод __str__ должен возвращать название группы"""
        self.assertEqual(self.group.title, self.group.__str__(),
                         'Метод __str__ не возвращает название группы')
