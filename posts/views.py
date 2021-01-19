from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User


# функция педженатора
def post_paginator(request, post_list):
    paginator = Paginator(post_list, settings.POSTS_IN_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return page, paginator


def index(request):
    post_list = Post.objects.select_related('group')
    page, paginator = post_paginator(request, post_list)
    return render(request,
                  'index.html', {'page': page, 'paginator': paginator})


# страница с списком всех групп
def group_post(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    page, paginator = post_paginator(request, post_list)

    return render(request, 'posts/group.html',
                  {'group': group,
                   'page': page,
                   'paginator': paginator})


# страница для создания новых постов
@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if request.GET or not form.is_valid():
        return render(request, 'posts/post_new_edit.html', {'form': form})

    post = form.save(commit=False)
    post.author = request.user
    form.save()
    return redirect('index')


# страница индивидуальных постов
def post_view(request, username, post_id):
    form = CommentForm(request.POST or None)
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id, author=author)
    comments = Comment.objects.filter(post_id=post_id)
    followers_count = Follow.objects.filter(
        author__username=username).select_related('follower').count()
    followers_list = Follow.objects.filter(author=author)
    return render(request, 'posts/post.html', {
        'post': post,
        'author': author,
        'form': form,
        'comments': comments,
        'followers_list': followers_list,
        'followers_count': followers_count,

    })


# страница редактирования постов. Доступ только для авторизованных.
@login_required()
def post_edit(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, author=author, id=post_id)
    # проверка на владельца поста.
    if request.user != author:
        return redirect(reverse('post', kwargs={'username': username,
                                                "post_id": post_id
                                                }))

    form = PostForm(request.POST or None, files=request.FILES or None,
                    instance=post)
    if request.method == 'POST' and form.is_valid():
        post.save()
        return redirect(reverse('post', kwargs={'username': username,
                                                'post_id': post_id}))

    return render(request, 'posts/post_new_edit.html', {'form': form,
                                                        'post': post,
                                                        'is_edit': True
                                                        })


# комментарии к посту
@login_required()
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if request.GET or not form.is_valid():
        return post_view(request, username, post_id)

    comment = form.save(commit=False)
    comment.author = request.user
    comment.post = post
    form.save()

    return redirect(reverse('post', kwargs={'username': username,
                                            'post_id': post_id}))


# страница подписанных авторов
@login_required
def follow_index(request):

    follow = Follow.objects.filter(
        user__username=request.user).select_related(
        'user').values_list('author_id')

    post_list = Post.objects.filter(author__in=follow)

    page, paginator = post_paginator(request, post_list)
    return render(request, "follow.html", {
        "page": page,
        "paginator": paginator,
    })


# функция подписки на пользователя
@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    # если пользователь не автор и запись отсутствует, создадим ее
    if request.user != author and not Follow.objects.filter(
            user=request.user, author=author).exists():
        Follow.objects.create(user=request.user, author=author)

    return redirect('profile', username=username)


# отписывание от пользователя
@login_required
def profile_unfollow(request, username):
    follower = Follow.objects.filter(
        author__username=username).select_related('follower'
                                                  )
    if follower.exists():
        follower.delete()
    return redirect('profile', username=username)


# страница профиля пользователя с списком постов
def profile(request, username):
    author = get_object_or_404(User, username=username)
    following = False
    if request.user.is_authenticated and \
            Follow.objects.filter(user=request.user, author=author).exists():
        following = True
    # лист подписчиков
    followers_count = Follow.objects.filter(
        author__username=username).select_related('follower').count()
    followers_list = Follow.objects.filter(author=author)
    post_list = author.posts.all()
    page, paginator = post_paginator(request, post_list)

    return render(request, 'posts/profile.html', {
        'page': page,
        'paginator': paginator,
        'profile': author,
        'following': following,
        'followers_list': followers_list,
        'followers_count': followers_count,
    })


# 404
def page_not_found(request, exception):
    return render(request,
                  'misc/404.html',
                  {'path': request.path},
                  status=404)


# 500
def server_error(request):
    return render(request,
                  'misc/500.html',
                  status=500)
