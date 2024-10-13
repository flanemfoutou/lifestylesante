from django.db import models
from profiles.models import Employe

#Create your models here.

class Log(models.Model):
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, blank=True, null=True)
    photo = models.ImageField(upload_to='logs')
    is_correct = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)