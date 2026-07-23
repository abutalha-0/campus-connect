from django.contrib import admin
from django.urls import path, include

admin.site.site_header = "Campus Connect Admin"
admin.site.site_title = "Campus Connect Admin"
admin.site.index_title = "Database Management"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.accounts.urls')),
    path('api/profiles/', include('users.student_profile.urls')),
    path('api/faculty/', include('users.faculty_profile.urls')),
    path('api/classroom/', include('classroom.subjects.urls')),
    path('api/classroom/', include('classroom.resources.urls')),
    path('api/classroom/', include('classroom.notices.urls')),
    path('api/classroom/', include('classroom.classes.urls')),
    path('api/classroom/', include('classroom.feed.urls')),
    path('api/classroom/', include('classroom.schedule.urls')),
]