from django.shortcuts import render
from .models import Job

# Create your views here.

def job_list(request):
    jobs = Job.objects.all().order_by("-created_at")
    return render(request, "jobs/job_list.html", {"jobs": jobs})
