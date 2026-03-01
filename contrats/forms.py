from django import forms
from .models import Contrat


class ContratEtape2Form(forms.ModelForm):
    class Meta:
        model  = Contrat
        fields = [
            'titre',
            'nom_client', 'email_client', 'telephone_client', 'adresse_client',
            'nom_prestataire', 'email_prestataire', 'telephone_prestataire', 'adresse_prestataire',
            'objet', 'montant', 'devise',
            'date_debut', 'date_fin',
            'lieu_signature', 'clauses_speciales',
        ]
        widgets = {
            'titre'               : forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Contrat de prestation Avril 2025'}),
            'nom_client'          : forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom complet ou raison sociale'}),
            'email_client'        : forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@exemple.ci'}),
            'telephone_client'    : forms.TextInput(attrs={'class': 'form-control', 'placeholder': '07 01 02 03 04'}),
            'adresse_client'      : forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'nom_prestataire'     : forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom complet ou raison sociale'}),
            'email_prestataire'   : forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@exemple.ci'}),
            'telephone_prestataire': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '07 01 02 03 04'}),
            'adresse_prestataire' : forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'objet'               : forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Décrivez précisément l\'objet du contrat...'}),
            'montant'             : forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'}),
            'devise'              : forms.TextInput(attrs={'class': 'form-control', 'value': 'FCFA'}),
            'date_debut'          : forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_fin'            : forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'lieu_signature'      : forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Abidjan, Côte d\'Ivoire'}),
            'clauses_speciales'   : forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Ajoutez des clauses particulières si nécessaire...'}),
        }
        labels = {
            'titre'                : 'Titre du contrat *',
            'nom_client'           : 'Nom du client / Preneur *',
            'email_client'         : 'Email du client',
            'telephone_client'     : 'Téléphone du client',
            'adresse_client'       : 'Adresse du client',
            'nom_prestataire'      : 'Nom du prestataire / Bailleur *',
            'email_prestataire'    : 'Email du prestataire',
            'telephone_prestataire': 'Téléphone du prestataire',
            'adresse_prestataire'  : 'Adresse du prestataire',
            'objet'                : 'Objet du contrat *',
            'montant'              : 'Montant',
            'devise'               : 'Devise',
            'date_debut'           : 'Date de début',
            'date_fin'             : 'Date de fin',
            'lieu_signature'       : 'Lieu de signature',
            'clauses_speciales'    : 'Clauses particulières',
        }

    def clean(self):
        cleaned = super().clean()
        date_debut = cleaned.get('date_debut')
        date_fin   = cleaned.get('date_fin')
        if date_debut and date_fin and date_fin < date_debut:
            raise forms.ValidationError('La date de fin ne peut pas être antérieure à la date de début.')
        return cleaned