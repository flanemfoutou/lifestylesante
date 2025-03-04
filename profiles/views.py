from django.shortcuts import render, get_object_or_404,redirect
from django.contrib.auth import login
import json
from pyzbar.pyzbar import decode
from PIL import Image
from .models import Employe  # Assurez-vous que le modèle Employe est correctement importé
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import login, logout
from django.contrib import messages
from django.utils import timezone
from django.utils import timezone
from .models import Employe
from .forms import MarquerArriveeForm,MarquerDepartForm



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
            return redirect('profil')

        except json.JSONDecodeError:
            return render(request, 'login.html', {"error": "Invalid QR code format"})
        except Exception as e:
            return render(request, 'login.html', {"error": f"Failed to authenticate: {str(e)}"})

    # Pour les requêtes GET
    return render(request, 'login.html')

@login_required
def profil_view(request):
    try:
        employe = Employe.objects.get(user=request.user)
    except ObjectDoesNotExist:
        # Utilisation d'ObjectDoesNotExist pour capturer toutes les exceptions de type 'DoesNotExist'
        return redirect('login')  # Assurez-vous que cette vue existe bien

    return render(request, 'profil.html', {'employe': employe})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def marquer_arrivee(request, employe_id):
    employe = get_object_or_404(Employe, id=employe_id)
    
    if request.method == 'POST':
        form = MarquerArriveeForm(request.POST)
        if form.is_valid():
            presence = form.save(commit=False)
            presence.employe = employe
            presence.date_arrivee = timezone.now()
            
            try:
                presence.save()
                messages.success(
                    request,
                    "Votre arrivée a bien été enregistrée avec succès. Merci beaucoup de votre ponctualité. "
                    "N'oubliez pas de signaler votre départ avant de partir."
                )

                # Déconnecter l'utilisateur
                logout(request)
                
                # Rediriger vers la page de connexion
                return redirect('login')

            except ValueError as e:
                messages.error(request, str(e))
                return redirect('login')
        else:
            messages.error(request, "Veuillez corriger les erreurs du formulaire.")

    else:
        form = MarquerArriveeForm(initial={'employe': employe})
    
    return render(request, 'marquer_arrivee.html', {'form': form, 'employe': employe})

@login_required
def marquer_depart(request, employe_id):
    employe = get_object_or_404(Employe, id=employe_id)
    
    if request.method == 'POST':
        form = MarquerDepartForm(request.POST)
        if form.is_valid():
            depart = form.save(commit=False)
            depart.employe = employe
            depart.date_depart = timezone.now()
            try:
                depart.save()  # Peut lever ValueError si le pointage est hors créneau ou déjà effectué
                messages.success(request, "Votre départ a été enregistré avec succès. Merci beaucoup et à demain !")  # Correction ici
                return redirect('login')
            except ValueError as e:
                messages.error(request, str(e))
                return redirect('login')
        else:
            messages.error(request, "Veuillez corriger les erreurs du formulaire.")
    else:
        form = MarquerDepartForm(initial={'employe': employe})

    return render(request, 'marquer_depart.html', {'form': form, 'employe': employe})
