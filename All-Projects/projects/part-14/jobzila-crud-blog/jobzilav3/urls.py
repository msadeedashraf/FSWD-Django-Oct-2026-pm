from django.contrib import admin
from django.urls import path, include
from . import views



urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("jobs/", include("jobs.urls")),
    path("blogs/", include("blogs.urls")),
    path("terms/", views.terms, name="terms"),
    path("privacy/", views.privacy, name="privacy"),
    path("contact/", views.contact, name="contact"),
    path("users/", include("users.urls")),
]
