from django import forms
from .models import Document

class DocumentForm(forms.ModelForm):
    class Meta:
        model  = Document
        fields = ['titre', 'categorie', 'description', 'fichier', 'statut']
        widgets = {
            'titre'      : forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Contrat fournisseur Mars 2026'}),
            'categorie'  : forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description optionnelle...'}),
            'fichier'    : forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png'}),
            'statut'     : forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'titre'      : 'Titre du document *',
            'categorie'  : 'Catégorie *',
            'description': 'Description',
            'fichier'    : 'Fichier * (PDF, Word, Excel, Image)',
            'statut'     : 'Visibilité',
        }

    def clean_fichier(self):
        fichier = self.cleaned_data.get('fichier')
        if fichier:
            ext = fichier.name.split('.')[-1].lower()
            if ext not in ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'jpeg', 'png']:
                raise forms.ValidationError('Format non supporté. Utilisez PDF, Word, Excel ou Image.')
            if fichier.size > 10 * 1024 * 1024:
                raise forms.ValidationError('Fichier trop volumineux. Maximum 10 Mo.')
        return fichier