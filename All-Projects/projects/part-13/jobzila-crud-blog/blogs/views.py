from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.shortcuts import render, redirect

from .forms import BlogForm

from .models import Blog

# Create your views here.

def blog(request):
    quick_search = request.GET.get("q", "").strip()

    
    blogs = Blog.objects.all().order_by("-date")

    if quick_search:
        blogs = blogs.filter(title__icontains=quick_search)


    return render(request, "blogs/blogs.html", {"blogs": blogs})

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
