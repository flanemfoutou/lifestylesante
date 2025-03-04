from django.urls import path
from .views import *

urlpatterns = [
  path('', profil_view, name='profil'),
  path('login/', authenticate_with_scanned_qr, name='login'),
  path('logout/', logout_view, name='logout'),
  path('employe/<int:employe_id>/arrivee/', marquer_arrivee, name='marquer_arrivee'),
  path('employe/<int:employe_id>/depart/', marquer_depart, name='marquer_depart'),  
    
]
