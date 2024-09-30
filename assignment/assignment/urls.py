from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import CustomLoginView, LogoutAPIView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', CustomLoginView.as_view(), name='login'),
    path('logout', LogoutAPIView.as_view(), name='logout'),
    path('accounts/', include('allauth.urls')), 
    path('api/', include('core.urls')),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


handler404 = 'core.views.custom_404'