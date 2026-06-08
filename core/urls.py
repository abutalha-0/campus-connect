from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.accounts.urls')),
    path('api/profiles/', include('users.student_profile.urls')),
]