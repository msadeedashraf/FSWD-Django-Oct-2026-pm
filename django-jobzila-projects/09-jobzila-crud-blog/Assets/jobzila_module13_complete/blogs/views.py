from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.text import slugify
from .author_mapping import editorial_team_for
from .forms import CreateBlogForm
from .models import Blog


def blog(request):
    blogs = Blog.objects.select_related('posted_by').order_by('-date')
    return render(request, 'blogs/blogs.html', {'blogs': blogs})


def blog_detail(request, blog_id):
    post = get_object_or_404(Blog.objects.select_related('posted_by'), pk=blog_id)
    return render(request, 'blogs/blog_detail.html', {'post': post})


def unique_slug(title, exclude_pk=None):
    base = (slugify(title) or 'article')[:40]
    slug = base
    index = 2
    qs = Blog.objects.all()
    if exclude_pk is not None:
        qs = qs.exclude(pk=exclude_pk)
    while qs.filter(slug=slug).exists():
        slug = f'{base}-{index}'
        index += 1
    return slug


@login_required(login_url='/users/login/')
def add_blog(request):
    form = CreateBlogForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.posted_by = request.user
        post.author = editorial_team_for(request.user)
        post.date = timezone.now()
        post.slug = unique_slug(post.title)
        post.save()
        return redirect('blogs:blog_detail', blog_id=post.pk)
    return render(request, 'blogs/add_blog.html', {'form': form})


@login_required(login_url='/users/login/')
def edit_blog(request, blog_id):
    post = get_object_or_404(Blog, pk=blog_id)
    if post.posted_by_id != request.user.pk:
        raise PermissionDenied
    form = CreateBlogForm(request.POST or None, request.FILES or None, instance=post)
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        # Keep slug stable so existing article links remain valid.
        post.save()
        return redirect('blogs:blog_detail', blog_id=post.pk)
    return render(request, 'blogs/edit_blog.html', {'form': form, 'post': post})


@login_required(login_url='/users/login/')
def delete_blog(request, blog_id):
    post = get_object_or_404(Blog, pk=blog_id)
    if post.posted_by_id != request.user.pk:
        raise PermissionDenied
    if request.method == 'POST':
        post.delete()
        return redirect('blogs:blogs')
    return render(request, 'blogs/delete_blog.html', {'post': post})
