from django.contrib.auth import get_user_model
from django.db import models
from django import forms

User = get_user_model()


class Group(models.Model):
    title = models.CharField('Заголовок',
                             max_length=200,
                             help_text='задайте заголовок')
    slug = models.SlugField(unique=True)
    description = models.TextField('Описание', max_length=400,
                                   help_text='описание группы. '
                                             'Не более 400 символов')

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField('Текст',
                            help_text='здесь можно писать свою историю')
    pub_date = models.DateTimeField('дата публикации',
                                    auto_now_add=True, )

    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='posts',
                               verbose_name='автор поста',
                               help_text='здесь указан автор поста')

    group = models.ForeignKey(Group, blank=True, null=True,
                              on_delete=models.SET_NULL,
                              related_name='posts',
                              verbose_name='сообщество',

                              help_text='здесь указано сообщество поста')
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(Post, blank=False, null=False,
                             on_delete=models.CASCADE,
                             related_name='comments')
    author = models.ForeignKey(User, blank=False, null=False,
                               on_delete=models.CASCADE,
                               related_name='comments')
    text = models.TextField('комментарий')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True,
                             null=True,
                             related_name='follower')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='following')
