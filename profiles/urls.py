from django.urls import path
from .views import *

urlpatterns = [
  path('', home_view, name='home'),
  path('login/', authenticate_with_scanned_qr, name='login'),
  path('logout/', logout_view, name='logout'),
  path("clsante/", DashboardView.as_view(), name="connexion"),
  path("déconnexion/", DeconnexionPageView.as_view(), name="deconnexion"),
  path("accueil",accueil, name ='accueil' ),
  path("dashboard/",dashboard, name ='dashboard' ),
  path("liste_employe/",liste_employe, name='liste_employe'),
  path('modifier/<int:pk>',modifier_employe, name= 'modifier_employe'),
  path('register/',register, name='register'), 
  path('employe/<int:employe_id>/arrivee/', marquer_arrivee, name='marquer_arrivee'),
  path('employe/<int:employe_id>/depart/', marquer_depart, name='marquer_depart'),  
  path('employe/<int:employe_id>/supprimer/',supprimer_employe, name='supprimer_employe'),
  
    # Vue pour afficher toutes les arrivées et départs
  path('liste/',liste_arrivees_departs, name='liste_arrivees_departs'),

    # Export CSV pour les arrivées
  path('export/arrivees/csv/',export_arrivees_csv, name='export_arrivees_csv'),
    
    # Export PDF pour les arrivées
  path('export/arrivees/pdf/',export_arrivees_pdf, name='export_arrivees_pdf'),
    
    # Export CSV pour les départs (ajoutez une vue similaire à celle des arrivées)
  path('export/departs/csv/',export_departs_csv, name='export_departs_csv'),
    
    # Export PDF pour les départs
  path('export/departs/pdf/',export_departs_pdf, name='export_departs_pdf'),
  
  


    
    
]
