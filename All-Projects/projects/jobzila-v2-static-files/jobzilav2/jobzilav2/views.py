from django.http import HttpResponse

def homepage(request):
    return HttpResponse("Welcome To JobZila Home Page")


def contact(request):
    return HttpResponse("Contact Jobzila")

