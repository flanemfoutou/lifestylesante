from django.contrib import admin
from .models import Employe, MarquerArrivee, MarquerDepart, RapportMensuel
import csv
import openpyxl  # Pour l'exportation en Excel
from django.http import HttpResponse
from django.utils.text import slugify  # Pour les noms de fichiers propres
from reportlab.pdfgen import canvas  # Pour l'export PDF

# Fonction d'export CSV
def export_as_csv(modeladmin, request, queryset):
    meta = modeladmin.model._meta
    field_names = [field.name for field in meta.fields]

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename={slugify(meta.verbose_name_plural)}.csv'
    
    writer = csv.writer(response)
    writer.writerow(field_names)  # En-têtes CSV
    
    for obj in queryset:
        writer.writerow([getattr(obj, field) for field in field_names])
    
    return response

export_as_csv.short_description = "Exporter en CSV"

# ✅ Fonction d'export Excel
def export_as_excel(modeladmin, request, queryset):
    meta = modeladmin.model._meta
    field_names = [field.name for field in meta.fields]
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(field_names)
    
    for obj in queryset:
        ws.append([getattr(obj, field) for field in field_names])
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename={slugify(meta.verbose_name_plural)}.xlsx'
    wb.save(response)
    return response

export_as_excel.short_description = "Exporter en Excel"

# Fonction pour restaurer les objets supprimés
def restore_selected_objects(modeladmin, request, queryset):
    queryset.update(is_deleted=False)

restore_selected_objects.short_description = "Restaurer les objets sélectionnés"

# Admin personnalisée pour inclure les objets supprimés
class BaseAdmin(admin.ModelAdmin):
    """
    Classe de base pour l'administration qui inclut la gestion des objets supprimés.
    """
    actions = [export_as_csv, export_as_excel, restore_selected_objects]  # Ajout des actions
    list_filter = ('is_deleted',)  # Ajout du filtre pour voir les objets supprimés
    
    def get_queryset(self, request):
        """
        Filtre par défaut pour exclure les objets supprimés, sauf si le filtre is_deleted=True est utilisé.
        """
        qs = super().get_queryset(request)
        if not request.GET.get('is_deleted__exact') == 'True':
            qs = qs.filter(is_deleted=False)
        return qs

#  Admin Employé
@admin.register(Employe)
class EmployeAdmin(BaseAdmin):
    list_display = ('user', 'nom', 'prenom', 'sexe', 'fonction', 'telephone', 'email')
    search_fields = ('nom', 'prenom', 'telephone', 'email', 'fonction')
    list_filter = ('sexe', 'fonction', 'departement', 'is_deleted')

#  Admin MarquerArrivee
@admin.register(MarquerArrivee)
class MarquerArriveeAdmin(BaseAdmin):
    list_display = ('employe', 'date_arrivee', 'arrivee', 'montant')
    list_filter = ('arrivee', 'date_arrivee', 'is_deleted')
    search_fields = ('employe__nom', 'employe__prenom', 'date_arrivee')
    ordering = ('-date_arrivee',)

#  Admin MarquerDepart
@admin.register(MarquerDepart)
class MarquerDepartAdmin(BaseAdmin):
    list_display = ('employe', 'date_depart', 'depart')
    list_filter = ('depart', 'date_depart', 'is_deleted')
    search_fields = ('employe__nom', 'employe__prenom', 'date_depart')
    ordering = ('-date_depart',)

#  Admin RapportMensuel
@admin.register(RapportMensuel)
class RapportMensuelAdmin(BaseAdmin):
    list_display = ('employe', 'mois', 'annee', 'total_arrivees', 'total_departs', 'total_montant')
    list_filter = ('mois', 'annee', 'is_deleted')
    search_fields = ('employe__nom', 'employe__prenom')
    ordering = ('-annee', '-mois')

