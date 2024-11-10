from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django_countries.fields import CountryField



class Employe(models.Model):
    
    GENRE = [
        ('F', 'Feminin'),
        ('M', 'Masculin')
    ]
    
    id = models.IntegerField(primary_key=True)  # Champ ID personnalisé sans AutoField
    matricule_employe = models.CharField(max_length=50, blank=True, null=True)
    photo = models.ImageField(upload_to='employe_photos/', blank=True, null=True)
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    genre = models.CharField(max_length=15, choices=GENRE)
    nationalite = CountryField()
    fonction = models.CharField(max_length=50)
    telephone = models.CharField(max_length=20)
    adresse = models.TextField()
    email = models.EmailField()
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.nom} {self.prenom}'

    @classmethod
    def generer_id(cls):
        # Récupère tous les IDs existants
        tous_ids = set(cls.objects.values_list('id', flat=True))
        
        # Cherche le premier ID disponible en partant de 1
        id = 1
        while id in tous_ids:
            id += 1
        return id

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = self.generer_id()  # Génère un ID si non défini
        if not self.matricule_employe:
            self.matricule_employe = self.generer_matricule()
        super().save(*args, **kwargs)

    @classmethod
    def generer_matricule(cls):
        tous_matricules = cls.objects.values_list('matricule_employe', flat=True)
        id = 1
        while True:
            matricule = f"CLSS-{id:04d}"
            if matricule not in tous_matricules:
                return matricule
            id += 1

class Connexion(models.Model):
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, blank=True, null=True)
    photo = models.ImageField(upload_to='logs')
    is_correct = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)
    

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
