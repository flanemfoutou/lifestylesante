import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from django_countries.fields import CountryField
from django.core.files.base import ContentFile
import qrcode
from io import BytesIO
import segno
from django.core.files.base import ContentFile
from pyzbar.pyzbar import decode
from PIL import Image
import json


class Employe(models.Model):
    SEXE_CHOICES = [
        ('F', 'Féminin'),
        ('M', 'Masculin'),
    ]

    # Informations personnelles
    nom = models.CharField(max_length=100, verbose_name="Nom")
    prenom = models.CharField(max_length=100, verbose_name="Prénom")
    sexe = models.CharField(max_length=1, choices=SEXE_CHOICES, verbose_name="Sexe")
    date_naissance = models.DateField(verbose_name="Date de naissance", blank=True, null=True)
    lieu_naissance = models.CharField(max_length=100, verbose_name="Lieu de naissance", blank=True, null=True)
    nationalite = CountryField(verbose_name="Nationalité")

    # Informations de contact
    adresse = models.TextField(verbose_name="Adresse")
    telephone = models.CharField(max_length=25, verbose_name="Téléphone")
    email = models.EmailField(verbose_name="Email")

    # Informations professionnelles
    fonction = models.CharField(max_length=100, verbose_name="Fonction", null=True)
    departement = models.CharField(max_length=100, verbose_name="Département", blank=True, null=True)
    photo = models.ImageField(upload_to='employe_photos/', blank=True, null=True, verbose_name="Photo")

    # Association avec un utilisateur
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Utilisateur")

    # QR Code et informations supplémentaires
    qr_code = models.ImageField(upload_to='qr_codes/', verbose_name="QR Code", blank=True, null=True)
    auth_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="Token d'authentification")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date et heure de création")

    def __str__(self):
        return f"{self.nom} {self.prenom} - {self.fonction}"


    def generate_qr_code(self):
        """
        Génère un QR code contenant les informations d'authentification via segno.
        """
        # Génère les données en format JSON pour le QR code
        qr_data = json.dumps({
            "auth_token": str(self.auth_token),
            "user_id": str(self.user.id),
        })

        # Génération du QR code avec segno
        qr = segno.make(qr_data, error='H')
        buffer = BytesIO()
        qr.save(buffer, kind='png', scale=10)
        buffer.seek(0)

        return ContentFile(buffer.read())
    
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
        
    def save(self, *args, **kwargs):
        """
        Sauvegarde l'objet Employe et régénère le QR code si auth_token ou user change.
        """
        if not self.qr_code or self._state.adding or self.auth_token_has_changed():
            qr_code_content = self.generate_qr_code()
            self.qr_code.save(f"qr_code_{self.id}.png", qr_code_content, save=False)

        super().save(*args, **kwargs)

    def auth_token_has_changed(self):
        """
        Vérifie si l'auth_token a changé.
        """
        if not self.pk:  # Si l'objet est nouveau
            return True
        original = Employe.objects.get(pk=self.pk)
        return original.auth_token != self.auth_token


class MarquerArrivee(models.Model):
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE)
    arrivee = models.BooleanField(default=True)
    date_arrivee = models.DateTimeField(auto_now_add=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return f"L'arrivée de {self.employe} | {self.arrivee} {self.date_arrivee} | ({self.latitude}, {self.longitude})"


class MarquerDepart(models.Model):
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE)
    depart = models.BooleanField(default=True)
    date_depart = models.DateTimeField(auto_now_add=True)
    date_arrivee = models.ForeignKey(MarquerArrivee, on_delete=models.CASCADE)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return f"Le départ de {self.employe} | {self.depart} {self.date_depart} | ({self.latitude}, {self.longitude})"
