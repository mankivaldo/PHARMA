from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import *

class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produits
        fields = ['name', 'categorie']

class AjoutProduits(forms.ModelForm):
    class Meta:
        model = Stockes
        fields = ['produit', 'quantite', 'price', 'condisionnement', 'description', 'lot' , 'date_expiration']
        widgets = {
            'date_expiration': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class AjoutVente(forms.Form):
    quantite = forms.IntegerField(min_value=1)
    customer = forms.CharField(max_length=100)

class InscriptionForm(forms.ModelForm):
    mot_de_passe = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mot de passe'
        }),
        required=True
    )
    confirmation_mot_de_passe = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmer le mot de passe'
        }),
        required=True
    )

    class Meta:
        model = Utilisateur
        fields = ['utilisateur', 'email']
        widgets = {
            'utilisateur': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom d\'utilisateur'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email'
            })
        }

    def clean(self):
        cleaned_data = super().clean()
        mot_de_passe = cleaned_data.get('mot_de_passe')
        confirmation_mot_de_passe = cleaned_data.get('confirmation_mot_de_passe')

        if mot_de_passe and confirmation_mot_de_passe and mot_de_passe != confirmation_mot_de_passe:
            raise forms.ValidationError("Les mots de passe ne correspondent pas")
        
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['mot_de_passe'])
        if commit:
            user.save()
        return user

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom d\'utilisateur'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mot de passe'
        })
    )

class VenteForm(forms.ModelForm):
    class Meta:
        model = Vente
        fields = ['customer', 'statupaiement', 'date_payement']
        widgets = {
            'date_payement': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        statupaiement = cleaned_data.get('statupaiement')
        date_payement = cleaned_data.get('date_payement')

        if statupaiement in ['C', 'CH'] and date_payement and date_payement.date() != now().date():
            raise forms.ValidationError("Pour un paiement en Cash ou Chèque, la date de paiement doit être aujourd'hui.")
        elif statupaiement == 'D' and date_payement and date_payement.date() <= now().date():
            raise forms.ValidationError("Pour un paiement en Dette, la date de paiement doit être supérieure à la date du jour.")
        return cleaned_data


class VenteProduitForm(forms.ModelForm):
    class Meta:
        model = VenteProduit
        fields = ['produit', 'quantite', 'prix_vente']

    def clean(self):
        cleaned_data = super().clean()
        produit = cleaned_data.get('produit')
        quantite = cleaned_data.get('quantite')

        if produit and quantite and quantite > produit.quantite:
            raise forms.ValidationError(f"Stock insuffisant. Disponible : {produit.quantite}")
        return cleaned_data