from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post
from django.core.cache import cache


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

    def test_post_added_in_index_page(self):
        """Тестирование наличия поста на главной странице сайта"""
        cache.clear()
        response = self.authorized_client.get(
            reverse('index'))
        post_id = response.context.get('page')[0].pk
        self.assertEqual(post_id, self.post.pk,
                         f'Созданный пост c pk={post_id} '
                         f'не был найден на странице "index"'
                         )

    def test_post_added_in_group_page(self):
        """Тестирование наличия поста присвоенного группе на странице группы"""
        post = Post.objects.first()

        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': f'{self.GROUP_SLUG}1'}))
        self.assertEqual(post.text, response.context.get('page')[0].text,
                         f'Запись {post} в группе'
                         f'{self.GROUP_SLUG} не найдена'
                         )

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
