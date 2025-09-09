from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import *
from django.utils import timezone

class CategorieForm(forms.ModelForm):
    class Meta:
        model = Categories
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
        }
        labels = {
            'name': 'Nom de la catégorie',
        }

class ConditionForm(forms.ModelForm):
    class Meta:
        model = Condition
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
        }
        labels = {
            'name': 'Nom de la condition',
        }

class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produits
        fields = ['name', 'categorie', 'slug']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'categorie': forms.Select(attrs={'class': 'form-control'}),
            'slug': forms.HiddenInput()
        }
        labels = {
            'name': 'Nom du produit',
            'categorie': 'Catégorie',
            'slug': 'Slug (généré automatiquement)'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].required = False


class AjoutVente(forms.Form):
    quantite = forms.IntegerField(min_value=1)
    customer = forms.CharField(max_length=100)

class InscriptionForm(UserCreationForm):
    telephone = forms.CharField(
        max_length=15, 
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Téléphone'
        })
    )
    adresse = forms.CharField(
        max_length=255, 
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Adresse'
        })
    )
    role = forms.ChoiceField(
        choices=CustomUser._meta.get_field('role').choices,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'telephone', 'adresse', 'role')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom d\'utilisateur'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email'
            })
        }

class UserEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'telephone', 'adresse', 'role')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = None # Masquer l'aide sur le nom d'utilisateur

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Nom d\'utilisateur'
        self.fields['password'].label = 'Mot de passe'

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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Exclure le statut 'Payé' des choix du formulaire de création/modification de vente
        form_choices = [
            choice for choice in Vente.PAYMENT_STATUS_CHOICES 
            if choice[0] != Vente.PAYMENT_STATUS_PAYER
        ]
        self.fields['statupaiement'].choices = [('', 'Choisissez le mode de paiement')] + form_choices
         # Force la valeur initiale à vide si ce n'est pas un POST (pour l'affichage du formulaire vierge)
        if not self.is_bound:
            self.fields['statupaiement'].initial = ''
    def clean(self):
        cleaned_data = super().clean()
        statupaiement = cleaned_data.get('statupaiement')
        date_payement = cleaned_data.get('date_payement')

        if not statupaiement:
            raise forms.ValidationError("Le mode de paiement est requis.")

        if statupaiement in ['C', 'CH']:
            # Pour Cash ou Chèque, on force la date à aujourd'hui
            cleaned_data['date_payement'] = timezone.now()
        elif statupaiement in ['D', 'OV']:
            # Validation pour une dette
            if not date_payement:
                raise forms.ValidationError("La date de paiement est requise pour une dette.")
            elif date_payement.date() <= timezone.now().date():
                raise forms.ValidationError("Pour une dette et ordre de virement, la date de paiement doit être dans le futur.")

        return cleaned_data


class VenteProduitForm(forms.ModelForm):
    class Meta:
        model = VenteProduit
        fields = ['produit', 'quantite', 'prix_vente'
        ]
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
            # Correction du chemin d'accès à la date d'expiration
            if produit.achat_ligne and produit.achat_ligne.date_expiration and produit.achat_ligne.date_expiration < timezone.now().date():
                raise forms.ValidationError("Ce produit est expiré")
            
        if prix_vente:
            if prix_vente <= 0:
                raise forms.ValidationError("Le prix de vente doit être supérieur à 0")
            if produit and produit.prix_achat and prix_vente < produit.prix_achat:
                raise forms.ValidationError("Le prix de vente ne peut pas être inférieur au prix d'achat")

        return cleaned_data
    
class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'NIF', 'phone', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'NIF': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'Nom complet',
            'NIF': 'NIF',
            'phone': 'Téléphone',
            'address': 'Adresse',
        }
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
        fields = ['produit', 'quantite', 'prix_achat', 'lot', 'date_expiration', 'conditionnement']
        widgets = {
            'produit': forms.Select(attrs={'class': 'form-control'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control'}),
            'prix_achat': forms.NumberInput(attrs={'class': 'form-control'}),
            'lot': forms.TextInput(attrs={'class': 'form-control'}),
            'date_expiration': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'conditionnement': forms.Select(attrs={'class': 'form-control'}),
            
        }
        labels = {
            'produit': 'Produit',
            'quantite': 'Quantité',
            'prix_achat': 'Prix d\'achat',
            'lot': 'Numéro de lot',
            'date_expiration': 'Date d\'expiration',
            'conditionnement': 'Conditionnement',
         
        }

class StockForm(forms.ModelForm):
    class Meta:
        model = Stockes
        fields = ['produit', 'quantite', 'stock_minimum', 'achat_ligne']
        widgets = {
            'produit': forms.Select(attrs={'class': 'form-control'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock_minimum': forms.NumberInput(attrs={'class': 'form-control'}),
            'achat_ligne': forms.Select(attrs={'class': 'form-control'})
        }
        labels = {
            'produit': 'Produit',
            'quantite': 'Quantité',
            'stock_minimum': 'Stock minimum',
            'achat_ligne': 'Ligne d\'achat'
        }

class AjustementStockForm(forms.Form):
    MOTIF_AJUSTEMENT_CHOICES = [
        ('', '---------'),
        ('RETOUR_CLIENT', 'Entrée - Retour client'),
        ('AJUSTEMENT_POSITIF', "Entrée - Ajustement d'inventaire"),
        ('PERTE_PEREMPTION', 'Sortie - Perte (Péremption)'),
        ('PERTE_CASSE', 'Sortie - Perte (Casse)'),
        ('PERTE_VOL', 'Sortie - Perte (Vol)'),
        ('AJUSTEMENT_NEGATIF', "Sortie - Ajustement d'inventaire"),
    ]

    stock = forms.ModelChoiceField(
        queryset=Stockes.objects.filter(quantite__gt=0).select_related('produit').order_by('produit__name'),
        label="Ligne de stock à ajuster",
        widget=forms.Select(attrs={
            'class': 'form-control',
            'data-live-search': 'true'
        })
    )
    motif = forms.ChoiceField(
        choices=MOTIF_AJUSTEMENT_CHOICES,
        label="Motif de l'ajustement",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    quantite = forms.IntegerField(
        min_value=1,
        label="Quantité à ajuster",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 5'})
    )
    raison = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Détails supplémentaires sur la raison de cet ajustement...'
        }),
        required=False,
        label="Détails (optionnel)"
    )

    def clean(self):
        cleaned_data = super().clean()
        stock = cleaned_data.get('stock')
        motif = cleaned_data.get('motif')
        quantite = cleaned_data.get('quantite')

        if motif and quantite and stock:
            # Pour les sorties, vérifier que la quantité n'excède pas le stock
            if motif in ['PERTE_PEREMPTION', 'PERTE_CASSE', 'PERTE_VOL', 'AJUSTEMENT_NEGATIF']:
                if quantite > stock.quantite:
                    raise forms.ValidationError(
                        f"La quantité à retirer ({quantite}) ne peut pas être supérieure au stock actuel ({stock.quantite})."
                    )
        return cleaned_data
