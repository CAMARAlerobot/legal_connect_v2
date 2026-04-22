from django import forms
from .models import Document

FORMATS_ACCEPTES = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'jpeg', 'png']
TAILLE_MAX_MB    = 10


class DocumentForm(forms.ModelForm):
    class Meta:
        model  = Document
        fields = [
            'titre', 'categorie', 'statut', 'description',
            'fichier', 'mots_cles', 'numero_reference', 'date_expiration',
        ]
        widgets = {
            'titre'           : forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Contrat fournisseur Mars 2026',
            }),
            'categorie'       : forms.Select(attrs={'class': 'form-select'}),
            'statut'          : forms.Select(attrs={'class': 'form-select'}),
            'description'     : forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3,
                'placeholder': 'Description optionnelle du document...',
            }),
            'fichier'         : forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png',
            }),
            'mots_cles'       : forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: contrat, fournisseur, 2026',
            }),
            'numero_reference': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: REF-2026-001',
            }),
            'date_expiration' : forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
        }
        labels = {
            'titre'           : 'Titre du document *',
            'categorie'       : 'Catégorie *',
            'statut'          : 'Visibilité',
            'description'     : 'Description',
            'fichier'         : 'Fichier *',
            'mots_cles'       : 'Mots-clés',
            'numero_reference': 'N° de référence',
            'date_expiration' : 'Date d\'expiration',
        }

    def clean_fichier(self):
        fichier = self.cleaned_data.get('fichier')
        if fichier and hasattr(fichier, 'name'):
            ext = fichier.name.split('.')[-1].lower()
            if ext not in FORMATS_ACCEPTES:
                raise forms.ValidationError(
                    f'Format non supporté. Formats acceptés : {", ".join(FORMATS_ACCEPTES).upper()}'
                )
            if fichier.size > TAILLE_MAX_MB * 1024 * 1024:
                raise forms.ValidationError(
                    f'Fichier trop volumineux. Maximum autorisé : {TAILLE_MAX_MB} Mo.'
                )
        return fichier


class VersionNoteForm(forms.Form):
    note = forms.CharField(
        max_length=300, required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Note sur les changements (optionnel)...',
        }),
        label='Note de version',
    )
