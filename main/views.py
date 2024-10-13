from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views import View
from django.contrib.auth import login, logout, authenticate
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.http import JsonResponse, HttpResponseBadRequest
from .utils import  classify_face
import base64
from logs.models import Log
from django.core.files.base import ContentFile
from django.contrib.auth.models import User
from profiles.models import Employe


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
    # Vérifiez si la requête est AJAX
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        photo = request.POST.get('photo')
        if not photo:
            return JsonResponse({'success': False, 'error': 'No photo provided'})

        try:
            # Décodage de l'image base64
            _, str_img = photo.split(';base64')
            decoded_file = base64.b64decode(str_img)

            # Sauvegarde de l'image dans le modèle Log
            x = Log()
            x.photo.save('upload.png', ContentFile(decoded_file))
            x.save()

            # Classification faciale
            res = classify_face(x.photo.path)
            if res:
                # Vérification de l'existence de l'utilisateur
                user_exists = User.objects.filter(username=res).exists()
                if user_exists:
                    user = User.objects.get(username=res)
                    employe = Employe.objects.get(user=user)

                    # Associer l'employé et sauvegarder
                    x.employe = employe
                    x.save()

                    # Connexion de l'utilisateur
                    login(request, user)
                    return JsonResponse({'success': True})
                else:
                    return JsonResponse({'success': False, 'error': 'User not found'})

            return JsonResponse({'success': False, 'error': 'Face not recognized'})

        except Exception as e:
            # Gérer les erreurs lors du traitement de l'image ou de la classification
            return JsonResponse({'success': False, 'error': str(e)})

    # Si la requête n'est pas AJAX, renvoyer une réponse 400 (mauvaise requête)
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

