from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('voyti-adminka-shamshoda/', admin.site.urls),
    path('', include('randomizer.urls')),
]
