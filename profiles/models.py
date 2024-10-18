from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django_countries.fields import CountryField


class Employe(models.Model):
    
    GENRE = [
    ('F','Feminin'),
    ('M','Masculin')
]
    
    matricule_employe = models.CharField(max_length=50, unique=True, blank=True, null=True)
    photo = models.ImageField(upload_to='employe_photos/', blank=True, null=True)
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    genre = models.CharField(max_length=15, choices=GENRE)
    nationalite = CountryField()
    fonction = models.CharField(max_length=50)
    telephone = models.CharField(max_length=20)
    adresse = models.CharField(max_length=50)
    email = models.EmailField()
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.nom} {self.prenom}'

    @classmethod
    def generer_matricule(cls):
        dernier_employe = cls.objects.order_by('-id').first()
        if dernier_employe:
            id = dernier_employe.id + 1
        else:
            id = 1
        matricule = f"CLSS-{id:04d}"
        return matricule

    def save(self, *args, **kwargs):
        if not self.matricule_employe:
            self.matricule_employe = self.generer_matricule()
        super().save(*args, **kwargs)


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
    date_arrivee = models.DateTimeField(auto_now_add="True")
    

    def __str__(self):
        return f"L'arrivée de {self.employe}  | {self.arrivee} {self.date_arrivee}" 

    
class MarquerDepart(models.Model):
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE)
    depart = models.BooleanField(default=True)
    date_depart = models.DateTimeField(auto_now_add="True")
    date_arrivee = models.ForeignKey(MarquerArrivee,on_delete=models.CASCADE)
    

    def __str__(self):
        return f"Le départ de {self.employe} |{self.depart}  {self.date_depart}" 

    






