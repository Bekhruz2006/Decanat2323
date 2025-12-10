from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import NewsListView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', NewsListView.as_view(), name='home'),
    path('accounts/', include('accounts.urls')),
    path('students/', include('decanat.urls')),
    path('curriculum/', include('decanat.urls_curriculum')),
    path('journal/', include('journal.urls')),
    path('schedule/', include('schedule.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)