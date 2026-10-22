from django.http import HttpResponse


def home(request):
    return HttpResponse("Hello World! Welcome to Django.")

def about(request):
    return HttpResponse("This is my About page.")

def contact(request):
    return HttpResponse("Contact us at hello@example.com")


def student(request):
    return HttpResponse(
        "Hello! My name is John and I am learning Django."
    )