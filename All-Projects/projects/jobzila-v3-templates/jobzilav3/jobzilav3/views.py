from django.shortcuts import render




def home(request):
    return render(request, "home.html")


def job_search(request):
    return render(request, "job_search.html")


def job_listing(request):
    return render(request, "job_listing.html")


def terms(request):
    return render(request, "terms.html")


def privacy(request):
    return render(request, "privacy.html")


def contact(request):
    return render(request, "contact_us.html")