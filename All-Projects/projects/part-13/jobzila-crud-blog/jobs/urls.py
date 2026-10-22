from django.urls import path

from . import views


app_name = "jobs"


urlpatterns = [
    path("", views.job_list, name="job_list"),
    path("add/", views.add_job, name="add_job"),
    path("<int:job_id>/", views.job_detail, name="job_detail"),
    path(
        "<int:job_id>/edit/",
        views.edit_job,
        name="edit_job",
    ),

    path(
        "<int:job_id>/delete/",
        views.delete_job,
        name="delete_job",
    ),

]