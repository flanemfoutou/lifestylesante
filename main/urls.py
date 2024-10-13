
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from .views import (
    login_view,
    logout_view,
    home_view,
    find_user_view,DasboardView,DeconnexionPageView
)

urlpatterns = [
    path('conix/', admin.site.urls),
    path('', home_view, name='home'),
    path('clinique/',include('profiles.urls')),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('classify/', find_user_view, name='classify'),
    path("connexion/", DasboardView.as_view(), name="connexion"),
    path("déconnexion/", DeconnexionPageView.as_view(), name="deconnexion"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

