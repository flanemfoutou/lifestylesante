from django import forms
from .models import MarquerArrivee, MarquerDepart


   
class MarquerArriveeForm(forms.ModelForm):
    class Meta:
        model = MarquerArrivee
        fields = ['arrivee']
       

class MarquerDepartForm(forms.ModelForm):
    class Meta:
        model = MarquerDepart
        fields = ['depart']


