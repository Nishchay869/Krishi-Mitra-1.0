from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from accounts.views import home

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('chat/', include('chatbot.urls')),
    path('crops/', include('crops.urls')),
    path('disease/', include('disease.urls')),
    path('weather/', include('weather.urls')),
    path('market/', include('market.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
