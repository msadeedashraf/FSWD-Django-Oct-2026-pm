from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from .forms import BlogForm
from .models import Blog

# Create your views here.

def blog(request):
    quick_search = request.GET.get("q", "").strip()

    
    blogs = Blog.objects.all().order_by("-date")

    if quick_search:
        blogs = blogs.filter(title__icontains=quick_search)


    return render(
    request,
    "blogs/blogs.html",
    {
        "blogs": blogs,
        "quick_search": quick_search,
    },
)

@login_required(login_url="/users/login/")
def add_blog(request):
    if request.method == "POST":
        form = BlogForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():
            blog = form.save(commit=False)

            # Use this only if author is a text field
            blog.author = request.user.username

            blog.save()

            return redirect(
                "blogs:blog_detail",
                blog_id=blog.id,
            )

    else:
        form = BlogForm()

    return render(
        request,
        "blogs/add_blog.html",
        {
            "form": form,
        },
    )


def blog_detail(request, blog_id):
    selected_blog = get_object_or_404(Blog, id=blog_id)

    return render(
        request,
        "blogs/blog_detail.html",
        {
            "blog": selected_blog,
        },
    )


@login_required(login_url="/users/login/")
def edit_blog(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)

    # Blog.author is currently a text field containing the username.
    if blog.author != request.user.username:
        raise PermissionDenied

    if request.method == "POST":
        form = BlogForm(
            request.POST,
            request.FILES,
            instance=blog,
        )

        if form.is_valid():
            updated_blog = form.save(commit=False)

            # Prevent someone from changing the author.
            updated_blog.author = request.user.username
            updated_blog.save()

            return redirect(
                "blogs:blog_detail",
                blog_id=blog.id,
            )

    else:
        form = BlogForm(instance=blog)

    return render(
        request,
        "blogs/edit_blog.html",
        {
            "form": form,
            "blog": blog,
        },
    )


@login_required(login_url="/users/login/")
def delete_blog(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)

    # Only the blog author can delete the blog.
    if blog.author != request.user.username:
        raise PermissionDenied

    if request.method == "POST":
        blog.delete()

        return redirect("blogs:blog")

    return render(
        request,
        "blogs/delete_blog.html",
        {
            "blog": blog,
        },
    )