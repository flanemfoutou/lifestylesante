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
import base64
import os
import uuid
from .utils import get_cached_encoded_faces
from django.conf import settings
from django.contrib.auth import login
from django.core.cache import cache
import face_recognition as fr
import numpy as np
from django.core.exceptions import ObjectDoesNotExist



def login_view(request):
    return render(request, 'registration/login.html', {})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def home_view(request):
    try:
        employe = Employe.objects.get(user=request.user)
    except ObjectDoesNotExist:
        # Utilisation d'ObjectDoesNotExist pour capturer toutes les exceptions de type 'DoesNotExist'
        return redirect('login')  # Assurez-vous que cette vue existe bien

    return render(request, 'main.html', {'employe': employe})

# Tolerance level for more accurate face matching
FACE_MATCH_THRESHOLD = 0.35  # Réduit pour plus de précision

def decode_base64_image(photo):
    try:
        _, str_img = photo.split(';base64,')
        return base64.b64decode(str_img)
    except Exception as e:
        print(f"Error decoding image: {e}")
        return None

def find_user_view(request):
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        photo = request.POST.get('photo')
        if not photo:
            return JsonResponse({'success': False, 'error': 'No photo provided'})

        decoded_file = decode_base64_image(photo)
        if decoded_file is None:
            return JsonResponse({'success': False, 'error': 'Invalid image data'})

        photo_filename = f"{uuid.uuid4()}.png"
        logs_folder = os.path.join(settings.MEDIA_ROOT, 'logs')
        os.makedirs(logs_folder, exist_ok=True)
        photo_path = os.path.join(logs_folder, photo_filename)

        try:
            with open(photo_path, 'wb') as photo_file:
                photo_file.write(decoded_file)

            # Vérifiez le contenu du cache
            print("Fetching encoded faces from cache...")
            faces = get_cached_encoded_faces()
            print(f"Encoded faces: {faces}")

            # Classification de l'image
            res = classify_face(photo_path)
            print(f"Classification result: {res}")

            if res and res != "Unknown":
                try:
                    user = User.objects.get(username=res)
                    login(request, user)
                    return JsonResponse({'success': True})
                except User.DoesNotExist:
                    return JsonResponse({'success': False, 'error': 'User not found'})

            return JsonResponse({'success': False, 'error': 'Face not recognized'})

        except Exception as e:
            print(f"Error during face classification: {e}")
            return JsonResponse({'success': False, 'error': str(e)})

        finally:
            # Essayez de commenter cette ligne pour voir si cela affecte le comportement
             if os.path.exists(photo_path):
                 os.remove(photo_path)

    return HttpResponseBadRequest('Invalid request')


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
    