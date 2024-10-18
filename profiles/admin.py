from django.contrib import admin
from .models import Employe, Connexion, MarquerArrivee, MarquerDepart


class EmployeAdmin(admin.ModelAdmin):
    list_display = ('matricule_employe', 'nom', 'prenom', 'fonction', 'telephone', 'email', 'date_creation')
    search_fields = ('matricule_employe', 'nom', 'prenom', 'email')
    list_filter = ('fonction', 'date_creation')
    readonly_fields = ('date_creation', 'matricule_employe')


class MarquerArriveeAdmin(admin.ModelAdmin):
    list_display = ('employe', 'arrivee', 'date_arrivee')
    list_filter = ('arrivee', 'date_arrivee')


class MarquerDepartAdmin(admin.ModelAdmin):
    list_display = ('employe', 'depart', 'date_depart', 'date_arrivee')
    list_filter = ('depart', 'date_depart')

admin.site.register(Employe, EmployeAdmin)
admin.site.register(MarquerArrivee, MarquerArriveeAdmin)
admin.site.register(MarquerDepart, MarquerDepartAdmin)
admin.site.register(Connexion)


