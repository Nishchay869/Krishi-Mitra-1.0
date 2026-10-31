from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from accounts.views import home, service_worker, settings_view
from django.views.i18n import JavaScriptCatalog

urlpatterns = [
    path('service-worker.js', service_worker, name='service-worker'),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    path('', home, name='home'),
    path('settings/', settings_view, name='settings_direct'),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('chat/', include('chatbot.urls')),
    path('crops/', include('crops.urls')),
    path('disease/', include('disease.urls')),
    path('weather/', include('weather.urls')),
    path('market/', include('market.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
