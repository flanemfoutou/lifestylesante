from django.shortcuts import render, get_object_or_404,redirect
from django.contrib.auth import login
from django.core.files.uploadedfile import InMemoryUploadedFile
from io import BytesIO
import json
from django.views import View
from pyzbar.pyzbar import decode
from PIL import Image
from .models import Employe  # Assurez-vous que le modèle Employe est correctement importé
from .utils import scan_qr_code
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import login, logout, authenticate
from django.utils.decorators import method_decorator
from django.contrib import messages
from datetime import time
from django.utils import timezone
from datetime import timedelta
import csv
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.utils import timezone
from datetime import datetime, timedelta
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from .models import Employe,MarquerArrivee,MarquerDepart
from .forms import EmployeForm,MarquerArriveeForm,MarquerDepartForm,UserRegistrationForm



def scan_qr_code(file):
    """
    Analyse un QR code pour en extraire les données.
    """
    img = Image.open(file)
    decoded_objects = decode(img)

    for obj in decoded_objects:
        print("Type:", obj.type)
        print("Data:", obj.data.decode('utf-8'))

    if decoded_objects:
        return decoded_objects[0].data.decode('utf-8')
    return None

def authenticate_with_scanned_qr(request):
    if request.method == 'POST':
        qr_data = request.POST.get('qr_data')
        if not qr_data:
            return render(request, 'login.html', {"error": "No QR data found"})

        try:
            qr_data = json.loads(qr_data)
            auth_token = qr_data.get('auth_token')
            user_id = qr_data.get('user_id')

            if not auth_token or not user_id:
                return render(request, 'login.html', {"error": "Invalid QR code data"})

            # Valider et connecter l'utilisateur
            employe = get_object_or_404(Employe, auth_token=auth_token, user_id=user_id)
            login(request, employe.user)

            # Rediriger vers la page home après succès
            return redirect('home')

        except json.JSONDecodeError:
            return render(request, 'login.html', {"error": "Invalid QR code format"})
        except Exception as e:
            return render(request, 'login.html', {"error": f"Failed to authenticate: {str(e)}"})

    # Pour les requêtes GET
    return render(request, 'login.html')

@login_required
def home_view(request):
    try:
        employe = Employe.objects.get(user=request.user)
    except ObjectDoesNotExist:
        # Utilisation d'ObjectDoesNotExist pour capturer toutes les exceptions de type 'DoesNotExist'
        return redirect('login')  # Assurez-vous que cette vue existe bien

    return render(request, 'main.html', {'employe': employe})

def logout_view(request):
    logout(request)
    return redirect('login')

class DashboardView(View):
    def get(self, request):
        return render(request, "registration/connexion.html")
    
    def post(self, request):
        data = request.POST
        
        user_auth = authenticate(request, username=data.get('username'),
                                 password=data.get('password'))
        
        if not user_auth:
            messages.error(request, "Vos informations de connexion sont erronées...")
            return self.get(request)
        
        # Vérification que l'utilisateur est un super utilisateur
        if not user_auth.is_superuser:
            messages.error(request, "Vous n'avez pas la permission d'accéder à cette interface.")
            return self.get(request)
        
        login(request, user_auth)
        
        return redirect("dashboard")
    
        
@method_decorator(login_required, name='dispatch')
class DeconnexionPageView(View):
    def get(self, request):
        logout(request)
        return redirect("connexion")
    

def accueil(request):
    
    template = 'index.html'
    
    return render(request,template)

@login_required
def dashboard(request):
    template = 'tableau_bord/dashboard.html'
    return render(request,template)

def liste_employe(request):
    employes = Employe.objects.all()
    return render(request, 'tableau_bord/liste_employe.html', {'employes': employes})

def modifier_employe(request, pk):
    employe = get_object_or_404(Employe, pk=pk)

    if request.method == 'POST':
        form = EmployeForm(request.POST, request.FILES, instance=employe)
        if form.is_valid():
            nouveau_employe = form.save()
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
            # Créer l'utilisateur sans l'enregistrer immédiatement
            user = form.save(commit=False)

            # Vérifier si l'utilisateur a choisi de définir un mot de passe
            if form.cleaned_data.get('set_password'):
                user.set_password(form.cleaned_data['password'])
            else:
                # Laisser le mot de passe vide si l'option n'est pas cochée
                user.password = ''

            # Enregistrer l'utilisateur dans la base de données
            user.save()
            
            # Redirection après enregistrement réussi
            messages.success(request, "L'utilisateur a été enregistré avec succès.")
            return redirect('liste_employe')
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
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
    writer.writerow(['Numero de presence', 'Nom', 'Prenom', 'Genre', 'Nationalite', 'Fonction', 'Arrivee', 'Date et heure d\'arrivee'])
    for arrivee in MarquerArrivee.objects.all():
        writer.writerow([arrivee.id, arrivee.employe.nom, arrivee.employe.prenom, arrivee.employe.sexe, arrivee.employe.nationalite, arrivee.employe.fonction, arrivee.arrivee, arrivee.date_arrivee])
    return response

# Export PDF (utilisation de pdfkit)
def export_arrivees_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="arrivees.pdf"'

    p = canvas.Canvas(response)

    arrivees = MarquerArrivee.objects.all()
    y = 800
    p.drawString(100, y, "Nom | Prenom  | Genre | Nationalite | Fonction  | Arrivee | Date et heure d'arrivee")
    y -= 20
    for arrivee in arrivees:
        p.drawString(100, y, f" {arrivee.employe.nom} | {arrivee.employe.prenom} | {arrivee.employe.sexe} | {arrivee.employe.nationalite} | {arrivee.employe.fonction} | {arrivee.arrivee} | {arrivee.date_arrivee}")
        y -= 20

    p.showPage()
    p.save()

    return response

# Export CSV pour les départs
def export_departs_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="departs.csv"'
    writer = csv.writer(response)
    writer.writerow(['Numéro de presence', 'Nom', 'Prenom', 'Genre', 'Nationalite', 'Fonction', 'Depart', 'Date et heure de depart'])
    
    # Récupération des données des départs
    for depart in MarquerDepart.objects.all():
        writer.writerow([depart.id, depart.employe.nom, depart.employe.prenom, depart.employe.sexe, depart.employe.nationalite, depart.employe.fonction, depart.depart, depart.date_depart])
    
    return response

# Export PDF pour les départs (utilisation de pdfkit)
def export_departs_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="departs.pdf"'

    p = canvas.Canvas(response)

    departs = MarquerDepart.objects.all()
    y = 800
    p.drawString(100, y, " Nom | Prenom | Genre | Nationalite |Fonction | Depart | Date et heure de depart")
    y -= 20
    for depart in departs:
        p.drawString(100, y, f" {depart.employe.nom} | {depart.employe.prenom} | {depart.employe.sexe} | {depart.employe.nationalite} | {depart.employe.fonction}| {depart.depart} | {depart.date_depart}")
        y -= 20

    p.showPage()
    p.save()

    return response
