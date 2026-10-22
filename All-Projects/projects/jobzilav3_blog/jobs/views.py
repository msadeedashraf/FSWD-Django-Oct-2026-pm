from django.db.models import Q
from django.shortcuts import render, get_object_or_404

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

    # -------------------------------------
    # Quick search: title only
    # -------------------------------------
    if quick_search:
        jobs = jobs.filter(title__icontains=quick_search)

    # -------------------------------------
    # Advanced search: multiple filters
    # -------------------------------------
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

    # -------------------------------------
    # Sorting
    # -------------------------------------
    if sort == "oldest":
        jobs = jobs.order_by("created_at")

    elif sort == "title":
        jobs = jobs.order_by("title")

    elif sort == "company":
        jobs = jobs.order_by("company")

    else:
        jobs = jobs.order_by("-created_at")

    # Used to decide whether advanced search is active
    advanced_search_active = any(
        [title, company, location, keyword, sort != "newest"]
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
