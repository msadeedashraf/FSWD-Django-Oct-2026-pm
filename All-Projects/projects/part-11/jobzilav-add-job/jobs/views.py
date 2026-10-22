from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CreateJobForm
from .models import Job


def job_list(request):
    # Quick-search value
    quick_search = request.GET.get("q", "").strip()

    # Advanced-search values
    title = request.GET.get("title", "").strip()
    company = request.GET.get("company", "").strip()
    location = request.GET.get("location", "").strip()
    keyword = request.GET.get("keyword", "").strip()
    sort = request.GET.get("sort", "newest")

    jobs = Job.objects.all()

    # Quick search: title only
    if quick_search:
        jobs = jobs.filter(title__icontains=quick_search)

    # Advanced search
    if title:
        jobs = jobs.filter(title__icontains=title)

    if company:
        jobs = jobs.filter(company__icontains=company)

    if location:
        jobs = jobs.filter(location__icontains=location)

    if keyword:
        jobs = jobs.filter(
            Q(title__icontains=keyword)
            | Q(company__icontains=keyword)
            | Q(location__icontains=keyword)
            | Q(description__icontains=keyword)
        )

    # Sorting
    if sort == "oldest":
        jobs = jobs.order_by("created_at")
    elif sort == "title":
        jobs = jobs.order_by("title")
    elif sort == "company":
        jobs = jobs.order_by("company")
    else:
        jobs = jobs.order_by("-created_at")

    advanced_search_active = any(
        [
            title,
            company,
            location,
            keyword,
            sort != "newest",
        ]
    )

    context = {
        "jobs": jobs,
        "quick_search": quick_search,
        "title_search": title,
        "company_search": company,
        "location_search": location,
        "keyword_search": keyword,
        "sort": sort,
        "advanced_search_active": advanced_search_active,
        "result_count": jobs.count(),
    }

    return render(request, "jobs/job_list.html", context)


def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    return render(
        request,
        "jobs/job_detail.html",
        {"job": job},
    )


@login_required(login_url="/users/login/")
def add_job(request):
    if request.method == "POST":
        form = CreateJobForm(request.POST)

        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by = request.user
            job.save()

            return redirect("jobs:job_detail", job_id=job.id)

    else:
        form = CreateJobForm()

    return render(
        request,
        "jobs/add_job.html",
        {"form": form},
    )