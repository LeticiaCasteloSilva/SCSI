from django.contrib import admin
from django.urls import include, path

from core.views import HealthCheckView

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health'),
    path('admin/celery-panel/', include('dj_celery_panel.urls')),
    path('admin/', admin.site.urls),
]
