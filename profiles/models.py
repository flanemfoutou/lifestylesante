import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now,localtime
from datetime import datetime, timedelta
from django.utils.timezone import make_aware, is_aware, localtime
from django_countries.fields import CountryField
from django.core.files.base import ContentFile
import qrcode
from io import BytesIO
import segno
from django.core.files.base import ContentFile
from pyzbar.pyzbar import decode
from PIL import Image
import json
from decimal import Decimal




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
    user = models.OneToOneField(User,  on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Nom Utilisateur")

    # QR Code et informations supplémentaires
    qr_code = models.ImageField(upload_to='qr_codes/', verbose_name="QR Code", blank=True, null=True)
    auth_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="Token d'authentification")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date et heure de création")
    is_deleted = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nom} {self.prenom} - {self.fonction}"
    
    def soft_delete(self):
            """Marque l'employé comme supprimé au lieu de le supprimer réellement"""
            self.is_deleted = True
            self.save()

    def restore(self):
        """Restaure un employé supprimé"""
        self.is_deleted = False
        self.save()

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
    
    

def get_time_slot_interval(date_time):
    """
    Retourne l'intervalle horaire global auquel appartient l'heure de pointage :
    - "matin_1" pour 5h-6h30
    - "matin_2" pour 8h-8h30
    - "apres_midi" pour 15h-15h30
    - "soir" pour 20h-20h30
    """
    t = localtime(date_time)
    if t.hour == 5 or (t.hour == 6 and t.minute < 30):
        return "matin_1"
    elif t.hour == 9 and t.minute < 30:
        return "matin_2"
    elif t.hour == 15 and t.minute < 30:
        return "apres_midi"
    elif t.hour == 20 and t.minute < 30:
        return "soir"
    return None

def peut_pointer(employe, date_time, modele):
    """
    Vérifie que l'employé n'a pas déjà marqué une arrivée dans l'intervalle horaire de la journée.
    Cette restriction ne s'applique qu'aux arrivées (`MarquerArrivee`).
    """
    if modele != MarquerArrivee:
        return True  # On ne bloque pas les départs

    intervalle = get_time_slot_interval(date_time)
    if intervalle is None:
        return False  # Heure non valide

    t = localtime(date_time)
    date_du_jour = t.date()

    # Définition des bornes des intervalles horaires pour les arrivées
    if intervalle == "matin_1":
        debut_intervalle = t.replace(hour=5, minute=0, second=0, microsecond=0)
        fin_intervalle = t.replace(hour=6, minute=30, second=0, microsecond=0)
    elif intervalle == "matin_2":
        debut_intervalle = t.replace(hour=8, minute=0, second=0, microsecond=0)
        fin_intervalle = t.replace(hour=8, minute=30, second=0, microsecond=0)
    elif intervalle == "apres_midi":
        debut_intervalle = t.replace(hour=15, minute=0, second=0, microsecond=0)
        fin_intervalle = t.replace(hour=15, minute=30, second=0, microsecond=0)
    elif intervalle == "soir":
        debut_intervalle = t.replace(hour=20, minute=0, second=0, microsecond=0)
        fin_intervalle = t.replace(hour=20, minute=30, second=0, microsecond=0)

    # Assurez-vous que les dates sont "aware"
    if not is_aware(debut_intervalle):
        debut_intervalle = make_aware(debut_intervalle)
    if not is_aware(fin_intervalle):
        fin_intervalle = make_aware(fin_intervalle)

    # Vérification stricte pour éviter un deuxième pointage dans le même créneau
    deja_pointe = modele.objects.filter(
        employe=employe,  # Vérifier par ID d'employé
        date_arrivee__date=date_du_jour,
        date_arrivee__gte=debut_intervalle,
        date_arrivee__lt=fin_intervalle
    ).exists()

    # Si l'employé a déjà pointé dans cet intervalle, retour False (blocage)
    if deja_pointe:
        print(f"L'employé {employe.id} a déjà pointé dans l'intervalle {intervalle} le {date_du_jour}.")
        return False  # Bloque l'enregistrement dans le même créneau horaire

    # Si l'employé n'a pas encore pointé, on autorise le pointage
    return True  
      
class MarquerArrivee(models.Model):
    employe = models.ForeignKey('Employe', on_delete=models.SET_NULL, null=True, blank=True)
    arrivee = models.BooleanField(default=True)  
    date_arrivee = models.DateTimeField(auto_now_add=True)
    montant = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_deleted = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        """
        Vérifie le créneau et s'assure que l'employé n'a pas déjà pointé 
        dans ce créneau le jour même. 
        """
        intervalle = get_time_slot_interval(self.date_arrivee)
        if intervalle is None:
            self.arrivee = False  # Hors de l'intervalle, donc marqué comme non valide
        else:
            if not peut_pointer(self.employe, self.date_arrivee, MarquerArrivee):
                raise ValueError("Vous avez déjà pointé dans ce créneau horaire aujourd'hui.")
            
            # Si dans l'intervalle, l'arrivée est validée et le montant attribué
            self.arrivee = True
            self.montant = 2000.00 if intervalle == "soir" else 1000.00

        super().save(*args, **kwargs)

        # Mise à jour automatique du rapport mensuel si l'arrivée est valide
        if self.arrivee:
            mois = localtime(self.date_arrivee).month
            annee = localtime(self.date_arrivee).year
            rapport, created = RapportMensuel.objects.get_or_create(
                employe=self.employe,
                mois=mois,
                annee=annee
            )
            rapport.mettre_a_jour()

    def __str__(self):
        return f"Arrivée de {self.employe} | {self.date_arrivee} | {'Validée' if self.arrivee else 'Non Validée'}"

    def soft_delete(self):
        self.is_deleted = True
        self.save()

    def restore(self):
        self.is_deleted = False
        self.save()


class MarquerDepart(models.Model):
    employe = models.ForeignKey('Employe', on_delete=models.SET_NULL, null=True, blank=True)
    depart = models.BooleanField(default=True)  # Modifié par défaut à False
    date_depart = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        """
        Vérifie le créneau et s'assure que l'employé n'a pas déjà pointé
        son départ dans ce créneau le jour même.
        """
        intervalle = get_time_slot_interval(self.date_depart)
        if intervalle is None:
            self.depart = False  # Hors de l'intervalle, donc marqué comme non valide
        else:
            if not peut_pointer(self.employe, self.date_depart, MarquerDepart):
                raise ValueError("Vous avez déjà pointé le départ dans ce créneau horaire aujourd'hui.")
            
            self.depart = True  # Si valide, enregistrement du départ

        super().save(*args, **kwargs)

        # Mise à jour du rapport mensuel si le départ est validé
        if self.depart:
            mois = localtime(self.date_depart).month
            annee = localtime(self.date_depart).year
            rapport, created = RapportMensuel.objects.get_or_create(
                employe=self.employe,
                mois=mois,
                annee=annee
            )
            rapport.mettre_a_jour()

    def __str__(self):
        return f"Départ de {self.employe} | {self.date_depart} | {'Validé' if self.depart else 'Non Validé'}"

    def soft_delete(self):
        self.is_deleted = True
        self.save()

    def restore(self):
        self.is_deleted = False
        self.save()


class RapportMensuel(models.Model):
    employe = models.ForeignKey('Employe',  on_delete=models.SET_NULL, null=True, blank=True)
    mois = models.IntegerField()  # Mois du rapport
    annee = models.IntegerField()  # Année du rapport
    total_arrivees = models.IntegerField(default=0, verbose_name="Arrivées signalées")
    total_departs = models.IntegerField(default=0, verbose_name="Départs signalés")
    total_montant = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Gain mensuel")
    is_deleted = models.BooleanField(default=True)
    class Meta:
        unique_together = ('employe', 'mois', 'annee')

    def mettre_a_jour(self):
        """
        Met à jour les statistiques du rapport mensuel (nombre d'arrivées, de départs et montant cumulé)
        ainsi que la répartition par semaine.
        """
        date_debut = make_aware(datetime(self.annee, self.mois, 1))
        if self.mois == 12:
            date_fin = make_aware(datetime(self.annee + 1, 1, 1))
        else:
            date_fin = make_aware(datetime(self.annee, self.mois + 1, 1))

        arrivees = MarquerArrivee.objects.filter(
            employe=self.employe,
            date_arrivee__gte=date_debut,
            date_arrivee__lt=date_fin
        )

        departs = MarquerDepart.objects.filter(
            employe=self.employe,
            date_depart__gte=date_debut,
            date_depart__lt=date_fin
        )

        self.total_arrivees = arrivees.count()
        self.total_departs = departs.count()
        self.total_montant = sum(arr.montant for arr in arrivees)

        # Ajout de la sauvegarde après mise à jour
        self.save()

        
    def __str__(self):
        return (
            f"Rapport {self.mois}/{self.annee} - {self.employe} | "
            f"Arrivées: {self.total_arrivees} | Départs: {self.total_departs} | "
            f"Montant: {self.total_montant} XAF"
        )
    
    def soft_delete(self):
        self.is_deleted = True
        self.save()

    def restore(self):
        self.is_deleted = False
        self.save()


