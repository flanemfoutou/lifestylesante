from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Employe, MarquerArrivee, MarquerDepart


class EmployeForm(forms.ModelForm):
    class Meta:
        model = Employe
        fields = [
            'photo', 'nom', 'prenom', 'date_naissance', 'lieu_naissance', 'sexe', 'nationalite', 'fonction',
            'departement', 'telephone', 'email',  'adresse', 'user'
        ]
        widgets = {
            'date_naissance': forms.DateInput(
                attrs={'type': 'date', 'value': ''},  # Assurez-vous que le type est 'date'
                format='%Y-%m-%d'  # Format d'affichage de la date
            ),
            'adresse': forms.Textarea(attrs={'rows': 2}),
        }

    # Pour que la date_naissance soit affichée dans le champ lors de l'édition
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.date_naissance:
            self.fields['date_naissance'].widget.attrs['value'] = self.instance.date_naissance.strftime('%Y-%m-%d')


class MarquerArriveeForm(forms.ModelForm):
    class Meta:
        model = MarquerArrivee
        fields = ['arrivee', 'latitude', 'longitude']
        widgets = {
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }


class MarquerDepartForm(forms.ModelForm):
    class Meta:
        model = MarquerDepart
        fields = ['depart', 'latitude', 'longitude']
        widgets = {
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }


class UserRegistrationForm(forms.ModelForm):
    set_password = forms.BooleanField(
        required=False, 
        initial=False, 
        label='Définir un mot de passe'
    )
    password = forms.CharField(
        widget=forms.PasswordInput, 
        label="Mot de passe", 
        required=False
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput, 
        label="Confirmer le mot de passe", 
        required=False
    )
    
    class Meta:
        model = User
        fields = ['username', 'password']

    def clean(self):
        cleaned_data = super().clean()
        set_password = cleaned_data.get('set_password')
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        # Si l'utilisateur a choisi de définir un mot de passe, valider les champs
        if set_password:
            if not password:
                raise ValidationError("Le mot de passe est requis.")
            if password != confirm_password:
                raise ValidationError("Les mots de passe ne correspondent pas.")

        return cleaned_data
