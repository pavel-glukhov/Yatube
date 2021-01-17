import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Follow, Group, Post


class PostsViewTests(TestCase):
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
        Group.objects.bulk_create([
            Group(title=f'{cls.PAGE_GROUP}{i}',
                  slug=f'{cls.GROUP_SLUG}{i}',
                  description=f'{cls.GROUP_DESCR}{i}')
            for i in range(1, 3)]
        )

        cls.post = Post.objects.create(
            text=cls.PAGE_TEXT,
            author=cls.user,
            group=Group.objects.get(title=cls.PAGE_GROUP + '1')
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
                                        kwargs={
                                            'slug': f'{self.GROUP_SLUG}1'}),
            'posts/post_new_edit.html': reverse('new_post'),
        }

        for template, reverse_name in templates_url_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template,
                                        f'Проблема с шаблоном: {template}'
                                        f' reverse name: {reverse_name} '
                                        )

    def test_context_in_new_post_page(self):
        """ Тестирование содержания context в new_post"""

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
        response = self.authorized_client.get(reverse('index'))

        context_post = {
            self.PAGE_TEXT: response.context['page'][0].text,
            self.AUTH_USER_NAME: response.context['page'][0].author.username,
            f'{self.PAGE_GROUP}1': response.context['page'][0].group.title
        }

        for expected, value in context_post.items():
            with self.subTest():
                self.assertEqual(value, expected,
                                 'Данные переданные в context'
                                 'не соответствуют записям')

    def test_context_in_group_page(self):
        """ Тестирование содержания context в group"""
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': f'{self.GROUP_SLUG}1'}))

        # group передает словарь с двумя ключами posts и group,
        # проверим их содержание

        context_group = {
            self.PAGE_TEXT: response.context['page'][0].text,
            self.AUTH_USER_NAME: response.context['page'][0].author.username,
            f'{self.PAGE_GROUP}1': response.context['group'].title,
            f'{self.GROUP_SLUG}1': response.context['group'].slug,
            f'{self.GROUP_DESCR}1': response.context['group'].description
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
            f'{self.PAGE_GROUP}1': response.context.get('post').group.title,
        }

        for expected, value in context_edit_page.items():
            with self.subTest():
                self.assertEqual(value, expected, 'Данные переданные'
                                                  ' в context не'
                                                  ' соответствуют'
                                                  ' записям')

    def test_context_in_profile_page(self):
        """Тестирование содержания context для profile"""

        response = self.guest_user.get(
            reverse('profile',
                    kwargs={'username': self.AUTH_USER_NAME}))

        context_edit_page = {
            self.PAGE_TEXT: response.context['page'][0].text,
            f'{self.PAGE_GROUP}1': response.context['page'][0].group.title,
            self.AUTH_USER_NAME: response.context['page'][0].author.username,
        }

        for expected, value in context_edit_page.items():
            with self.subTest():
                self.assertEqual(value, expected, 'Данные переданные'
                                                  ' в context не'
                                                  ' соответствуют'
                                                  ' записям')

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
            f'{self.PAGE_GROUP}1': response.context.get('post').group.title,
            self.AUTH_USER_NAME: response.context.get('post').author.username,
        }

        for expected, value in context_edit_page.items():
            with self.subTest():
                self.assertEqual(value, expected, 'Данные переданные'
                                                  ' в context не'
                                                  ' соответствуют'
                                                  ' записям')

    def test_post_added_in_index_page(self):
        """Тестирование наличия поста на главной странице сайта"""

        response = self.authorized_client.get(
            reverse('index'))
        post_id = response.context.get('page')[0].pk
        self.assertEqual(post_id, self.post.pk,
                         f'Созданный пост c pk={post_id} '
                         f'не был найден на странице "index"')

    def test_post_added_in_group_page(self):
        """Тестирование наличия поста присвоенного группе на странице группы"""
        post = Post.objects.first()
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': f'{self.GROUP_SLUG}1'}))
        self.assertEqual(post.text, response.context.get('page')[0].text,
                         f'Запись {post} в группе'
                         f'{self.GROUP_SLUG} не найдена')

    def test_post_added_in_correct_group(self):
        """Тестирование на правильность назначения групп для постов"""
        # Созданный тестовый пост не должен содержаться не в своей группе.
        # Обратимся к группе test-group1, не содержит ли он иные записи
        # возьмем первую запись
        group = Group.objects.first()
        # исключим группу
        posts_out_of_group = Post.objects.exclude(group=group)
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': f'{self.GROUP_SLUG}1'}))

        group_list_exclude_posts_set = set(posts_out_of_group)
        # получим все записи в object_list
        all_posts_of_group_page = response.context.get(
            'paginator').object_list
        # проверим полученные значения на пересечение
        self.assertTrue(
            group_list_exclude_posts_set.isdisjoint(
                all_posts_of_group_page))


# тест подписывания пользователей друг на друга
class FollowUserTest(TestCase):
    FOLLOWER_POST_USER = 'TestUser_01'
    AUTHOR_POST_USER = 'TestUser_02'

    def setUp(self):
        # создадим 2х пользователей.
        self.auth_user = get_user_model().objects.create(
            username=self.FOLLOWER_POST_USER)
        self.author_post = get_user_model().objects.create(
            username=self.AUTHOR_POST_USER)

        # Создадим 2 записи на нашем сайте
        Post.objects.create(text='Тест',
                            author=self.author_post)

        Post.objects.create(text='Тест',
                            author=self.auth_user)

        # авторизуем подписчика
        self.auth_client_follower = Client()
        self.auth_client_follower.force_login(self.auth_user)

        # авторизуем владельца записи на нашем сайте
        self.auth_client_author = Client()
        self.auth_client_author.force_login(self.author_post)

    def test_authorized_user_follow_to_other_user(self):
        """Тестирование подписывания на пользователей"""
        self.auth_client_follower.post(reverse(
            'profile_follow',
            kwargs={
                'username': self.author_post
            }))
        self.assertTrue(Follow.objects.filter(user=self.auth_user,
                                              author=self.author_post),
                        'Подписка на пользователя не рабоатет')

    def test_authorized_user_unfollow(self):
        """Тестирование отписывания от пользователей"""
        self.auth_client_follower.get(reverse(
            'profile_unfollow',
            kwargs={
                'username': self.author_post
            }))

        self.assertFalse(Follow.objects.filter(user=self.auth_user,
                                               author=self.author_post),
                         'Отписка от пользователя не работает')

    def test_post_added_to_follow(self):
        """Тестирование на правильность работы подписывания на пользователя"""

        # подпишем пользователя на auth_client_author
        self.auth_client_follower.post(reverse(
            'profile_follow',
            kwargs={
                'username': self.author_post
            }))
        # получим все посты подписанного пользователя
        posts = Post.objects.filter(
            author__following__user=self.auth_user)

        response_follower = self.auth_client_follower.get(
            reverse('follow_index'))
        response_author = self.auth_client_author.get(
            reverse('follow_index'))

        # проверим содержание Context страницы follow_index пользователя
        # auth_client_follower и убедимся, что они имеются в ленте
        self.assertIn(posts.get(),
                      response_follower.context['paginator'].object_list,
                      'Запись отсутствует на странице подписок пользователя')

        # проверим содержание Context страницы follow_index пользователя
        # auth_client_author и убедимся, что записи в ленте не имеется
        self.assertNotIn(posts.get(),
                         response_author.context['paginator'].object_list,
                         'Запись добавлена к неверному пользователю.')


class PaginatorViewsTest(TestCase):
    """Тестируем Paginator. Страница должна быть разбита на 10 постов"""

    POSTS_COUNT = 13

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = get_user_model().objects.create(username='TestUser')

        Post.objects.bulk_create([Post(
            text=f'Тестовое сообщение{i}',
            author=cls.user)
            for i in range(cls.POSTS_COUNT)])

    def test_first_page_contains_ten_records(self):
        """Тестируем Paginator.Первые 10 постов на первой странице"""

        response = self.client.get(reverse('index'))
        self.assertEqual(
            len(response.context.get('page').object_list),
            settings.POSTS_IN_PAGE
        )

    def test_second_page_contains_three_records(self):
        """Тестируем Paginator.Последние 3 поста на второй странице"""

        response = self.client.get(reverse('index') + '?page=2')
        self.assertEqual(
            len(response.context.get('page').object_list),
            self.POSTS_COUNT - settings.POSTS_IN_PAGE
        )


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
                                         slug='test-group')
        cls.post = Post.objects.create(text='Тестовая запись',
                                       group=cls.group,
                                       author=cls.user,
                                       image=cls.uploaded)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()

    def test_context_index_page(self):
        """Проверяем context страницы index на наличие изображения"""
        response = self.guest_client.get(reverse('index'))
        response_data_image = response.context['page'][0].image
        expected = f'posts/{self.uploaded.name}'

        self.assertEqual(response_data_image,
                         expected, 'Изображение переданные'
                                   ' в context страницы index'
                                   ' не соответствует загруженному')

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
                                   ' не соответствует загруженному')

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
                                   ' не соответствует загруженному')

    def test_context_post_page(self):
        """Проверяем context страницы post на наличие изображения"""
        response = self.guest_client.get(
            reverse('post', kwargs={'username': self.AUTH_USER_NAME,
                                    'post_id': self.post.pk
                                    }
                    ))

        response_data_image = response.context['post'].image
        expected = f'posts/{self.uploaded.name}'

        self.assertEqual(response_data_image,
                         expected, 'Изображение переданное'
                                   ' в context страницы post'
                                   ' не соответствует загруженному')


# класс тестирования работоспособности кеширования страниц
class CacheViewTest(TestCase):
    AUTHORIZED_USER_NAME = 'TestUser'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = get_user_model().objects.create(
            username=cls.AUTHORIZED_USER_NAME
        )

        Post.objects.bulk_create([Post(text=f'Test{i}', author=cls.user)
                                  for i in range(5)])
        cls.guest_user = Client()

    def test_index_cache(self):
        """Тестирование работоспособности кеширования на странице Index"""
        response = self.guest_user.get(reverse('index'))
        Post.objects.bulk_create([Post(text=f'Test{i}', author=self.user)
                                  for i in range(3)])

        # Вычисление колличества записей context и колличества записей в базе
        context_cache_data_len = len(response.context.get('page').object_list)
        post_context_cache_len = Post.objects.count()

        # длина кеша должна отличаться от колличества записанных постов в базе
        self.assertNotEqual(context_cache_data_len, post_context_cache_len,
                            'Кеширование работает неправильно.'
                            ' Число записей в Context совпадает '
                            'с колличеством записей в базе')
        # очистим кеш и по новой запросим информацию с страницы
        cache.clear()
        response = self.guest_user.get(reverse('index'))
        # вычислим длину
        context_len = len(response.context.get('page').object_list)
        post_len = Post.objects.count()
        # колличество записей должно совпадать
        self.assertEqual(context_len, post_len,
                         'Кеширование работает неверно.'
                         ' Колличество записей после обновления'
                         ' не совпадает')
