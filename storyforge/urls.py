from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('stories.urls')),
]

handler404 = 'stories.views.error_404'
handler500 = 'stories.views.error_500'
