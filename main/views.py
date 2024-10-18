from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views import View
from django.contrib.auth import login, logout, authenticate
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.http import JsonResponse, HttpResponseBadRequest
from .utils import  classify_face
import base64
from django.core.files.base import ContentFile
from django.contrib.auth.models import User
import tempfile
import os
from django.conf import settings 
from profiles.models import Employe, Connexion

 

def login_view(request):
    return render(request, 'registration/login.html', {})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def home_view(request):
    employe = Employe.objects.get(user=request.user)
    return render(request, 'main.html', {'employe': employe})

def find_user_view(request):
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        photo = request.POST.get('photo')
        if not photo:
            return JsonResponse({'success': False, 'error': 'No photo provided'})

        try:
            # Décodage de la photo base64
            _, str_img = photo.split(';base64,')
            decoded_file = base64.b64decode(str_img)

            # Définir le chemin vers le dossier logs dans le dossier medias
            logs_folder = os.path.join(settings.MEDIA_ROOT, 'logs')
            if not os.path.exists(logs_folder):
                os.makedirs(logs_folder)

            # Sauvegarde de la photo temporairement dans le dossier medias/logs
            photo_path = os.path.join(logs_folder, 'temp_photo.png')
            with open(photo_path, 'wb') as photo_file:
                photo_file.write(decoded_file)

            # Classification faciale
            res = classify_face(photo_path)

            # Afficher le résultat de la classification pour le débogage
            print(f"Résultat de la classification : {res}")

            if res:
                user_exists = User.objects.filter(username=res).exists()
                if user_exists:
                    user = User.objects.get(username=res)
                    employe = Employe.objects.get(user=user)
                    login(request, user)

                    # Suppression de la photo après connexion réussie
                    if os.path.exists(photo_path):
                        os.remove(photo_path)

                    return JsonResponse({'success': True})
                else:
                    # Suppression de la photo en cas d'échec
                    if os.path.exists(photo_path):
                        os.remove(photo_path)
                    return JsonResponse({'success': False, 'error': 'User not found'})

            # Suppression de la photo en cas de non reconnaissance faciale
            if os.path.exists(photo_path):
                os.remove(photo_path)

            return JsonResponse({'success': False, 'error': 'Face not recognized'})

        except Exception as e:
            # Suppression de la photo en cas d'exception
            if os.path.exists(photo_path):
                os.remove(photo_path)
            return JsonResponse({'success': False, 'error': str(e)})

    return HttpResponseBadRequest('Invalid request')


class DasboardView(View):
    def get(self, request):
        return render(request, "registration/connexion.html")
    
    def post(self, request):
        data = request.POST
        
        user_auth = authenticate(request, username=data.get('username'),
                                 password=data.get('password'))
        
        if not  user_auth:
            messages.error(request,"Vos informations de connexions sont érronnées...")
            return self.get(request)
        
        login(request, user_auth)
        
        return redirect("dashboard")
 
        
@method_decorator(login_required, name='dispatch')
class DeconnexionPageView(View):
    def get(self, request):
        logout(request)
        return redirect("connexion")
    