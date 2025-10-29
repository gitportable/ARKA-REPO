import os
import sys
import subprocess
from pathlib import Path

def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"Created {path}")

BASE = Path.cwd() / "students_project"
VENV = BASE / "venv"

if not VENV.exists():
    subprocess.check_call([sys.executable, "-m", "venv", str(VENV)])
    print("Virtualenv created")

if sys.platform == "win32":
    pip = VENV / "Scripts" / "pip.exe"
    python = VENV / "Scripts" / "python.exe"
else:
    pip = VENV / "bin" / "pip"
    python = VENV / "bin" / "python"

subprocess.check_call([str(pip), "install", "--upgrade", "pip"])
subprocess.check_call([str(pip), "install", "Django==4.2.7", "djangorestframework==3.14.0"])
print("Dependencies installed")
manage = python  

if not (BASE / "manage.py").exists():
    subprocess.check_call([
        str(python), "-m", "django", "startproject",
        "students_project", str(BASE)
    ])
    print("Django project created")

os.chdir(BASE) 

students_app = BASE / "students"
if not students_app.exists():
    subprocess.check_call([str(manage), "startapp", "students"])
    print("App 'students' created")
write_file(BASE / "requirements.txt", """Django==4.2.7
djangorestframework==3.14.0
""")

# students_project/settings.py 
settings_py = """\
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "django-insecure-change-me-in-production"
DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "students",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "students_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "students_project.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
"""
write_file(BASE / "students_project" / "settings.py", settings_py)

# students_project/urls.py 
proj_urls = """\
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("students.urls")),
]
"""
write_file(BASE / "students_project" / "urls.py", proj_urls)

# students/models.py 
models_py = """\
from django.db import models

class Student(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
"""
write_file(students_app / "models.py", models_py)

#students/serializers.py
serializers_py = """\
from rest_framework import serializers
from .models import Student

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ["id", "name", "age", "email"]
"""
write_file(students_app / "serializers.py", serializers_py)

#students/views.py
views_py = """\
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Student
from .serializers import StudentSerializer

@api_view(["GET", "POST"])
def student_list(request):
    if request.method == "GET":
        students = Student.objects.all()
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data)

    if request.method == "POST":
        serializer = StudentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
"""
write_file(students_app / "views.py", views_py)

#students/urls.py
app_urls = """\
from django.urls import path
from . import views

urlpatterns = [
    path("students/", views.student_list, name="student_list"),
]
"""
write_file(students_app / "urls.py", app_urls)

#students/admin.py 
admin_py = """\
from django.contrib import admin
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("name", "age", "email")
    search_fields = ("name", "email")
    list_filter = ("age",)
"""
write_file(students_app / "admin.py", admin_py)
#students/apps.py
apps_py = """\
from django.apps import AppConfig

class StudentsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "students"
"""
write_file(students_app / "apps.py", apps_py)
subprocess.check_call([str(manage), "makemigrations"])
subprocess.check_call([str(manage), "migrate"])
print("Migrations applied")

# Uncomment if you want a superuser automatically
# subprocess.check_call([str(manage), "createsuperuser", "--noinput",
#                        "--username", "admin", "--email", "admin@example.com"])

#HAS TO BE RUN IN NEW PROCESS
print("\nAll files are ready!")
print("Starting Django development server at http://127.0.0.1:8000")
print("API endpoint: http://127.0.0.1:8000/api/students/\n")
os.execvp(str(manage), [str(manage), "runserver"])
