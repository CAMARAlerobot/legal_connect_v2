from django import forms
from django.contrib.auth.models import User
from .models import Profil, ROLES, SPECIALITES

ROLES_INSCRIPTION = [
    ('commercant',  'Commerçant'),
    ('prestataire', 'Prestataire de service'),
    ('expert',      'Expert (Juriste / Comptable)'),
]

class InscriptionForm(forms.ModelForm):
    password  = forms.CharField(
        label='Mot de passe *', min_length=6,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Min. 6 caractères'})
    )
    password2 = forms.CharField(
        label='Confirmer le mot de passe *',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Répétez le mot de passe'})
    )
    role = forms.ChoiceField(
        label='Je suis *', choices=ROLES_INSCRIPTION,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    telephone = forms.CharField(
        label='Téléphone', required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'id_telephone', 'placeholder': '07 01 02 03 04'})
    )
    entreprise = forms.CharField(
        label='Organisation', required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'id_entreprise', 'placeholder': 'Nom de votre structure'})
    )
    adresse = forms.CharField(
        label='Localité', required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'id_adresse', 'placeholder': 'Ville / Quartier'})
    )
    specialite = forms.ChoiceField(
        label='Spécialité', required=False,
        choices=[('', '— Choisir une spécialité —')] + list(SPECIALITES),
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_specialite'})
    )

    class Meta:
        model  = User
        fields = ['first_name', 'last_name', 'username', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom'}),
            'last_name' : forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom'}),
            'username'  : forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom d\'utilisateur'}),
            'email'     : forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@exemple.ci'}),
        }
        labels = {
            'first_name': 'Prénom *',
            'last_name' : 'Nom *',
            'username'  : 'Nom d\'utilisateur *',
            'email'     : 'Email *',
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Ce nom d\'utilisateur est déjà pris.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Cet email est déjà utilisé.')
        return email

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('password') != cleaned.get('password2'):
            raise forms.ValidationError('Les mots de passe ne correspondent pas.')
        return cleaned


class ProfilForm(forms.ModelForm):
    class Meta:
        model  = Profil
        fields = ['telephone', 'entreprise', 'adresse', 'bio']
        widgets = {
            'telephone' : forms.TextInput(attrs={'class': 'form-control'}),
            'entreprise': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse'   : forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'bio'       : forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }