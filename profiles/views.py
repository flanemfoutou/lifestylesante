from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import time
from django.utils import timezone
from datetime import timedelta
import csv
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.utils import timezone
from datetime import datetime, timedelta
from django.template.loader import render_to_string
from .models import Employe,MarquerArrivee,MarquerDepart
from .forms import EmployeForm,MarquerArriveeForm,MarquerDepartForm,UserRegistrationForm




def accueil(request):
    
    template = 'index.html'
    
    return render(request,template)

@login_required
def dashboard(request):
    template = 'tableau_bord/dashboard.html'
    return render(request,template)

def modifier_employe(request, pk):

    employe = get_object_or_404(Employe, pk=pk)

    if request.method == "POST":
        form = EmployeForm(request.POST,request.FILES, instance=employe)
        if form.is_valid():
            nouveau_employe = form.save()
            nouveau_employe.generer_matricule()

            return redirect('liste_employe')

    form = EmployeForm(instance=employe)

    template = 'tableau_bord/ajouter_employe.html'
    context={
        "form" : form
    }
    return render(request, template, context)

def liste_employe(request):
    employes = Employe.objects.all()
    return render(request, 'tableau_bord/liste_employe.html', {'employes': employes})

def modifier_employe(request, pk):
    employe = get_object_or_404(Employe, pk=pk)

    if request.method == 'POST':
        form = EmployeForm(request.POST, request.FILES, instance=employe)
        if form.is_valid():
            nouveau_employe = form.save()
            nouveau_employe.generer_matricule()
            return redirect('liste_employe')
    else:
        form = EmployeForm(instance=employe)

    return render(request, 'tableau_bord/modifier_employe.html', {'form': form})

def supprimer_employe(request, employe_id):
    employe = get_object_or_404(Employe, id=employe_id)
    
    # Vérifie si la demande est une confirmation de suppression
    if request.method == "POST":
        employe.delete()
        return redirect('liste_employe')
    
    # Affiche la page de confirmation si non confirmé
    return render(request, 'confirmer_suppression.html', {'employe': employe})
  
@login_required
def marquer_arrivee(request, employe_id):
    employe = get_object_or_404(Employe, id=employe_id)
    if request.method == 'POST':
        form = MarquerArriveeForm(request.POST)
        if form.is_valid():
            presence = form.save(commit=False)
            presence.employe = employe
            presence.date_arrivee = timezone.now()
            presence.save()
            messages.success(request, "Votre arrivée a été marquée.")
            return redirect('accueil')
    else:
        form = MarquerArriveeForm(initial={'employe': employe})
    return render(request, 'marquer_arrivee.html', {'form': form, 'employe': employe})

@login_required
def marquer_depart(request, employe_id):
    employe = get_object_or_404(Employe, id=employe_id)
    arrivee = MarquerArrivee.objects.filter(employe=employe).last()  # Récupère la dernière arrivée de l'employé

    if not arrivee:
        messages.error(request, "L'heure d'arrivée n'a pas été trouvée. Veuillez marquer votre arrivée avant de marquer votre départ.")
        return redirect('marquer_arrivee', employe_id=employe_id)

    if request.method == 'POST':
        form = MarquerDepartForm(request.POST)
        if form.is_valid():
            depart = form.save(commit=False)
            depart.employe = employe
            depart.date_depart = timezone.now()
            depart.date_arrivee = arrivee  # Associe l'heure d'arrivée avec le départ
            depart.save()
            messages.success(request, "Votre départ a été marqué.")
            return redirect('accueil')
    else:
        form = MarquerDepartForm(initial={'employe': employe})

    return render(request, 'marquer_depart.html', {'form': form, 'employe': employe})

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Créer l'utilisateur sans l'enregistrer directement dans la base de données
            user = form.save(commit=False)
            # Définir le mot de passe
            user.set_password(form.cleaned_data['password'])
            user.save()  # Enregistrer l'utilisateur dans la base de données
            return redirect('liste_employe')  # Redirection après inscription
    else:
        form = UserRegistrationForm()

    return render(request, 'tableau_bord/register.html', {'form': form})

# Vue pour afficher tout
def liste_arrivees_departs(request):
    arrivees = MarquerArrivee.objects.all()
    departs = MarquerDepart.objects.all()
    return render(request, 'liste_presence.html', {'arrivees': arrivees, 'departs': departs})



# Export CSV
def export_arrivees_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="arrivees.csv"'
    writer = csv.writer(response)
    writer.writerow(['Numero de presence', 'Matricule', 'Nom', 'Prenom', 'Genre', 'Nationalite', 'Fonction', 'Arrivee', 'Date et heure d\'arrivee'])
    for arrivee in MarquerArrivee.objects.all():
        writer.writerow([arrivee.id, arrivee.employe.matricule_employe, arrivee.employe.nom, arrivee.employe.prenom, arrivee.employe.genre, arrivee.employe.nationalite, arrivee.employe.fonction, arrivee.arrivee, arrivee.date_arrivee])
    return response

# Export PDF (utilisation de pdfkit)
def export_arrivees_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="arrivees.pdf"'

    p = canvas.Canvas(response)

    arrivees = MarquerArrivee.objects.all()
    y = 800
    p.drawString(100, y, "Matricule | Nom | Prenom  | Genre | Nationalite | Fonction  | Arrivee | Date et heure d'arrivee")
    y -= 20
    for arrivee in arrivees:
        p.drawString(100, y, f"{arrivee.employe.matricule_employe} | {arrivee.employe.nom} | {arrivee.employe.prenom} | {arrivee.employe.genre} | {arrivee.employe.nationalite} | {arrivee.employe.fonction} | {arrivee.arrivee} | {arrivee.date_arrivee}")
        y -= 20

    p.showPage()
    p.save()

    return response

# Export CSV pour les départs
def export_departs_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="departs.csv"'
    writer = csv.writer(response)
    writer.writerow(['Numéro de presence', 'Matricule', 'Nom', 'Prenom', 'Genre', 'Nationalite', 'Fonction', 'Depart', 'Date et heure de depart'])
    
    # Récupération des données des départs
    for depart in MarquerDepart.objects.all():
        writer.writerow([depart.id, depart.employe.matricule_employe, depart.employe.nom, depart.employe.prenom, depart.employe.genre, depart.employe.nationalite, depart.employe.fonction, depart.depart, depart.date_depart])
    
    return response

# Export PDF pour les départs (utilisation de pdfkit)
def export_departs_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="departs.pdf"'

    p = canvas.Canvas(response)

    departs = MarquerDepart.objects.all()
    y = 800
    p.drawString(100, y, "Matricule | Nom | Prenom | Genre | Nationalite |Fonction | Depart | Date et heure de depart")
    y -= 20
    for depart in departs:
        p.drawString(100, y, f"{depart.employe.matricule_employe} | {depart.employe.nom} | {depart.employe.prenom} | {depart.employe.genre} | {depart.employe.nationalite} | {depart.employe.fonction}| {depart.depart} | {depart.date_depart}")
        y -= 20

    p.showPage()
    p.save()

    return response