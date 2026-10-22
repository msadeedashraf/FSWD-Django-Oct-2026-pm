from django.urls import path
from . import views

app_name = "blogs"

urlpatterns = [
    path("", views.blog, name="blog"),
    path("add/", views.add_blog, name="add_blog"),
    path("<int:blog_id>/", views.blog_detail, name="blog_detail"),
    
    
     path(
        "<int:blog_id>/edit/",
        views.edit_blog,
        name="edit_blog",
    ),

    path(
        "<int:blog_id>/delete/",
        views.delete_blog,
        name="delete_blog",
    ),
]