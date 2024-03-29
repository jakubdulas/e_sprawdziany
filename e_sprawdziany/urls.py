from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('school/', include('teacher.urls')),
    path('student/', include('student.urls')),
    path('test/', include('tests.urls')),
    path('administration/', include('administration.urls')),
    path('message/', include('directmessages.urls')),
    path('', include('general.urls')),
]

if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)