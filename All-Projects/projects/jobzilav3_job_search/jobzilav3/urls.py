from django.contrib import admin
from django.urls import path, include
from . import views

from . import views


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("job-search/", views.job_search, name="job_search"),
    path("job-listing/", views.job_listing, name="job_listing"),
    path("jobs/", include("jobs.urls")),
    path("terms/", views.terms, name="terms"),
    path("privacy/", views.privacy, name="privacy"),
    path("contact/", views.contact, name="contact"),
]
