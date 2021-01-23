from django.contrib import admin

from .models import Comment, Group, Post, Follow
from django.utils.html import format_html


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'pub_date', 'author', 'group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'

    readonly_fields = ['image_tag', ]

    def image_tag(self, instance):
        return format_html(
            '<img src="{0}" style="max-width: 40%"/>',
            instance.image.url
        )


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('title', 'description',)
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}
    empty_value_display = '-пусто-'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'text', 'created',)
    search_fields = ('author', 'text',)
    empty_value_display = '-пусто-'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    empty_value_display = '-пусто-'
