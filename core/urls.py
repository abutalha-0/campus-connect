from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.accounts.urls')),
    path('api/profiles/', include('users.student_profile.urls')),
    path('api/crew/', include('crew.urls')),
    path('api/notifications/', include('notifications.urls')),
]
