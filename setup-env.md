>py --version

>pip install pipenv

create a project folder 

>mkdir hello-world
>cd hello-world

>py -m venv .venv

Activate the env
>.\.venv\Scripts\activate

>(.venv) PS D:\hello-world> py -m pip install Django

To create the django project
>django-admin startproject helloworld

>cd helloworld
>py .\manage.py runserver 8001

create views.py file with the following code

from django.http import HttpResponse


def homepage(request):
    return HttpResponse("Welcome to CBC!")


def about(request):
    return HttpResponse("This is our about page text")


update the urls.py file with the following changes

from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.homepage),
    path("about/", views.about),

![Emmit Include Languages](Assets/emmit.png)

### App and Templates

start the env

>cd helloworld

>py .\manage.py startapp posts

### Create a django app
![Step 1](/Assets/create-new-project-step1.png)
![Step 2](/Assets/create-new-project-step2.png)
![Step 3](/Assets/create-new-project-step3.png)
![Step 4](/Assets/create-new-project-step4.png)



>py .\manage.py migrate
>py .\manage.py makemigrations

>py .\manage.py shell 

>>> from posts.models import Post
>>> p = Post()
>>> p
>>> p.title = "My First post"
>>> p.save()

>>> Post.objects.all()
>>> Post.objects.all().values()


now test admin 
http://127.0.0.1:8005/admin/login/?next=/admin/


to create a super user

>py .\manage.py createsuperuser

jobzila
Pa55w.rd


py -m pip install Pillow

To rollback the database to the last script
py .\manage.py migrate <app name> zero

py .\manage.py migrate posts zero
py .\manage.py migrate


delete the db.sqlite3 file
py .\manage.py makemigration
py .\manage.py migrate

py .\manage.py createsuperuser

### SQL Lite browser

[SQL Lite](https://sqlitebrowser.org/dl/)

Click > DB Browser for SQLite - Standard installer for 64-bit Windows

### Final Project

Syed and Charline
[Marketplace](https://www.freecodecamp.org/news/learn-django-by-building-a-marketplace/)


Fatima, Slah
[CRM](https://www.youtube.com/watch?v=t10QcFx7d5k&ab_channel=freeCodeCamp.org)


### Django Rest API


>py -m venv .venv 
>.\.venv\Scripts\activate   
>pip install django djangorestframework
>djanjo-admin startproject newapiproject
> cd newapiproject
> py .\manage.py startapp sample_api 
> newapiproject/settings.py

INSTALLED_APPS = [  
    'django.contrib.admin',  
    'django.contrib.auth',  
    'django.contrib.contenttypes',  
    'django.contrib.sessions',  
    'django.contrib.messages',  
    'django.contrib.staticfiles',  
    'rest_framework',  
    'sample_api',  
] 


# to initialize the database   
python manage.py migrate   
# to open the prompt  
python manage.py createsuperuser  

username:sadeed