from django.shortcuts import render
from .models import Blog

# Create your views here.

def blog(request):
    blogs = Blog.objects.all().order_by("-date")
    return render(request, "blogs/blogs.html", {"blogs": blogs})
