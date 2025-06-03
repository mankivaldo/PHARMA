from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import *

class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produits
        fields = ['name', 'categorie']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'categorie': forms.Select(attrs={'class': 'form-control'})
        }
        labels = {
            'name': 'Nom du produit',
            'categorie': 'Catégorie'
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
            'date_payement': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'statupaiement': forms.Select(attrs={
                'class': 'form-control'
            })
        }
        labels = {
            'customer': 'Client',
            'statupaiement': 'Mode de paiement',
            'date_payement': 'Date de paiement'
        }

    def clean(self):
        cleaned_data = super().clean()
        statupaiement = cleaned_data.get('statupaiement')
        date_payement = cleaned_data.get('date_payement')

        if not statupaiement:
            raise forms.ValidationError("Le mode de paiement est requis.")

        if statupaiement in ['C', 'CH']:
            # Pour Cash ou Chèque, on force la date à aujourd'hui
            cleaned_data['date_payement'] = timezone.now()
        elif statupaiement == 'D':
            # Validation pour une dette
            if not date_payement:
                raise forms.ValidationError("La date de paiement est requise pour une dette.")
            elif date_payement.date() <= timezone.now().date():
                raise forms.ValidationError("Pour une dette, la date de paiement doit être dans le futur.")

        return cleaned_data


class VenteProduitForm(forms.ModelForm):
    class Meta:
        model = VenteProduit
        fields = ['produit', 'quantite', 'prix_vente']
        widgets = {
            'produit': forms.Select(attrs={
                'class': 'form-control',
                'data-live-search': 'true'
            }),
            'quantite': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'prix_vente': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            })
        }
        labels = {
            'produit': 'Article',
            'quantite': 'Quantité',
            'prix_vente': 'Prix unitaire'
        }

    def clean(self):
        cleaned_data = super().clean()
        produit = cleaned_data.get('produit')
        quantite = cleaned_data.get('quantite')
        prix_vente = cleaned_data.get('prix_vente')

        if produit and quantite:
            if quantite <= 0:
                raise forms.ValidationError("La quantité doit être supérieure à 0")
            if quantite > produit.quantite:
                raise forms.ValidationError(f"Stock insuffisant. Disponible : {produit.quantite}")
            if produit.date_expiration and produit.date_expiration < timezone.now().date():
                raise forms.ValidationError("Ce produit est expiré")
            
        if prix_vente:
            if prix_vente <= 0:
                raise forms.ValidationError("Le prix de vente doit être supérieur à 0")
            if produit and produit.prix_achat and prix_vente < produit.prix_achat:
                raise forms.ValidationError("Le prix de vente ne peut pas être inférieur au prix d'achat")

        return cleaned_data
    
class FournisseurForm(forms.ModelForm):
    class Meta:
        model = Fournisseur
        fields = ['nom', 'contact', 'adresse']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'contact': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse': forms.TextInput(attrs={'class': 'form-control'})
        }
        labels = {
            'nom': 'Nom du fournisseur',
            'contact': 'Contact',
            'adresse': 'Adresse'
        }

    def clean_contact(self):
        contact = self.cleaned_data.get('contact')
        if contact and len(contact.strip()) < 8:
            raise forms.ValidationError("Le numéro de contact doit contenir au moins 8 caractères")
        return contact

class AchatForm(forms.ModelForm):
    class Meta:
        model = Achat
        fields = ['fournisseur', 'date_achat', 'facture']
        widgets = {
            'fournisseur': forms.Select(attrs={'class': 'form-control'}),
            'date_achat': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'facture': forms.TextInput(attrs={'class': 'form-control'})
        }
        labels = {
            'fournisseur': 'Fournisseur',
            'date_achat': 'Date d\'achat',
            'facture': 'Numéro de facture'
        }

    def clean_facture(self):
        facture = self.cleaned_data.get('facture')
        if facture and Achat.objects.filter(facture=facture).exists():
            raise forms.ValidationError("Ce numéro de facture existe déjà")
        return facture

class AchatLigneForm(forms.ModelForm):
    class Meta:
        model = AchatLigne
        fields = ['produit', 'quantite', 'prix_achat', 'lot', 'date_expiration', 'conditionnement', 'description']
        widgets = {
            'produit': forms.Select(attrs={'class': 'form-control'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control'}),
            'prix_achat': forms.NumberInput(attrs={'class': 'form-control'}),
            'lot': forms.TextInput(attrs={'class': 'form-control'}),
            'date_expiration': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'conditionnement': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
        }
        labels = {
            'produit': 'Produit',
            'quantite': 'Quantité',
            'prix_achat': 'Prix d\'achat',
            'lot': 'Numéro de lot',
            'date_expiration': 'Date d\'expiration',
            'conditionnement': 'Conditionnement',
            'description': 'Description'
        }

class StockForm(forms.ModelForm):
    class Meta:
        model = Stockes
        fields = ['produit', 'quantite', 'prix_vente', 'stock_minimum', 'achat_ligne']
        widgets = {
            'produit': forms.Select(attrs={'class': 'form-control'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control'}),
            'prix_vente': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock_minimum': forms.NumberInput(attrs={'class': 'form-control'}),
            'achat_ligne': forms.Select(attrs={'class': 'form-control'})
        }
        labels = {
            'produit': 'Produit',
            'quantite': 'Quantité',
            'prix_vente': 'Prix de vente',
            'stock_minimum': 'Stock minimum',
            'achat_ligne': 'Ligne d\'achat'
        }

class AjustementStockForm(forms.Form):
    stock = forms.ModelChoiceField(
        queryset=Stockes.objects.all(),
        label="Ligne de stock à ajuster",
        widget=forms.Select(attrs={
            'class': 'form-control',
            'data-live-search': 'true'
        })
    )
    nouvelle_quantite = forms.IntegerField(
        min_value=0,
        label="Nouvelle quantité",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    type_modification = forms.ChoiceField(
        choices=ModificationStock.TYPE_CHOICES,
        label="Type de modification",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    raison = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Expliquez la raison de cet ajustement...'
        }),
        required=True,
        label="Raison de l'ajustement"
    )

    def clean(self):
        cleaned_data = super().clean()
        stock = cleaned_data.get('stock')
        nouvelle_quantite = cleaned_data.get('nouvelle_quantite')
        raison = cleaned_data.get('raison')

        if not raison or len(raison.strip()) < 10:
            raise forms.ValidationError("Une raison détaillée (minimum 10 caractères) est requise pour l'ajustement")

        if stock and nouvelle_quantite is not None:
            if nouvelle_quantite < 0:
                raise forms.ValidationError("La quantité ne peut pas être négative")
            if nouvelle_quantite == stock.quantite:
                raise forms.ValidationError("La nouvelle quantité est identique à l'ancienne")

        return cleaned_data

