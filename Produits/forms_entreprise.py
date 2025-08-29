from django import forms
from .models import Entreprise

class EntrepriseForm(forms.ModelForm):
    class Meta:
        model = Entreprise
        fields = ['nom', 'nif', 'nc', 'nom_tva', 'adresse', 'telephone', 'info_bancaire', 'logo']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'nif': forms.TextInput(attrs={'class': 'form-control'}),
            'nc': forms.TextInput(attrs={'class': 'form-control'}),
            'nom_tva': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse': forms.TextInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'info_bancaire': forms.TextInput(attrs={'class': 'form-control'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'nom': 'Nom de l’entreprise',
            'nif': 'NIF',
            'nc': 'NC',
            'nom_tva': 'Nom assujetti à la TVA',
            'adresse': 'Adresse',
            'telephone': 'Téléphone',
            'info_bancaire': 'Informations bancaires',
            'logo': 'Logo',
        }
