from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Employe, MarquerArrivee,MarquerDepart


class EmployeForm(forms.ModelForm):
    class Meta:
        model = Employe
        fields = ['photo','nom','prenom','genre','nationalite','fonction','telephone','bio','adresse','email','user']


class MarquerArriveeForm(forms.ModelForm):
    class Meta:
        model = MarquerArrivee
        fields = ['arrivee']
    
    
class MarquerDepartForm(forms.ModelForm):
    class Meta:
        model = MarquerDepart
        fields = ['depart']


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Mot de passe")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirmer le mot de passe")

    class Meta:
        model = User
        fields = ['username']

    # Validation pour vérifier que les mots de passe correspondent
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise ValidationError("Les mots de passe ne correspondent pas.")

        return cleaned_data


