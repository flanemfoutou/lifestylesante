# Generated by Django 5.1.4 on 2025-03-04 21:15

import django.db.models.deletion
import django_countries.fields
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Employe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100, verbose_name='Nom')),
                ('prenom', models.CharField(max_length=100, verbose_name='Prénom')),
                ('sexe', models.CharField(choices=[('F', 'Féminin'), ('M', 'Masculin')], max_length=1, verbose_name='Sexe')),
                ('date_naissance', models.DateField(blank=True, null=True, verbose_name='Date de naissance')),
                ('lieu_naissance', models.CharField(blank=True, max_length=100, null=True, verbose_name='Lieu de naissance')),
                ('nationalite', django_countries.fields.CountryField(max_length=2, verbose_name='Nationalité')),
                ('adresse', models.TextField(verbose_name='Adresse')),
                ('telephone', models.CharField(max_length=25, verbose_name='Téléphone')),
                ('email', models.EmailField(max_length=254, verbose_name='Email')),
                ('fonction', models.CharField(max_length=100, null=True, verbose_name='Fonction')),
                ('departement', models.CharField(blank=True, max_length=100, null=True, verbose_name='Département')),
                ('photo', models.ImageField(blank=True, null=True, upload_to='employe_photos/', verbose_name='Photo')),
                ('qr_code', models.ImageField(blank=True, null=True, upload_to='qr_codes/', verbose_name='QR Code')),
                ('auth_token', models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="Token d'authentification")),
                ('date_creation', models.DateTimeField(auto_now_add=True, verbose_name='Date et heure de création')),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Nom Utilisateur')),
            ],
        ),
        migrations.CreateModel(
            name='MarquerArrivee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('arrivee', models.BooleanField(default=True)),
                ('date_arrivee', models.DateTimeField(auto_now_add=True)),
                ('montant', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('employe', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='profiles.employe')),
            ],
        ),
        migrations.CreateModel(
            name='MarquerDepart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('depart', models.BooleanField(default=True)),
                ('date_depart', models.DateTimeField(auto_now_add=True)),
                ('employe', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='profiles.employe')),
            ],
        ),
        migrations.CreateModel(
            name='RapportMensuel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mois', models.IntegerField()),
                ('annee', models.IntegerField()),
                ('total_arrivees', models.IntegerField(default=0, verbose_name='Arrivées signalées')),
                ('total_departs', models.IntegerField(default=0, verbose_name='Départs signalés')),
                ('total_montant', models.DecimalField(decimal_places=2, default=0.0, max_digits=10, verbose_name='Gain mensuel')),
                ('employe', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='profiles.employe')),
            ],
            options={
                'unique_together': {('employe', 'mois', 'annee')},
            },
        ),
    ]
