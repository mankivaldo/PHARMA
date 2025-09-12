from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
import re

# Modèle pour les informations de l'entreprise
class Entreprise(models.Model):
    nom = models.CharField(max_length=255)
    nif = models.CharField(max_length=100)
    nc = models.CharField(max_length=100)
    nom_tva = models.CharField(max_length=255, blank=True, null=True)
    adresse = models.CharField(max_length=255)
    telephone = models.CharField(max_length=50, blank=True, null=True)
    info_bancaire = models.CharField(max_length=255, blank=True, null=True)
    logo = models.ImageField(upload_to='image/', blank=True, null=True)

    def __str__(self):
        return self.nom

class CustomUser(AbstractUser):
    telephone = models.CharField(max_length=15, blank=True, null=True)
    adresse = models.CharField(max_length=255, blank=True, null=True)
    role = models.CharField(
        max_length=20,
        choices=[
            ('ADMIN', 'Administrateur'),
            ('VENDEUR', 'Vendeur'),
            ('GESTIONNAIRE', 'Gestionnaire de stock')
        ],
        default='VENDEUR'
    )
    date_creation = models.DateTimeField(auto_now_add=True, null=True)
    derniere_connexion = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        db_table = 'produits_customuser'  # Explicitly set the table name

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        if not self.id:
            self.date_creation = timezone.now()
        super().save(*args, **kwargs)

class Categories(models.Model):
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"


from django.utils.text import slugify

class Produits(models.Model):
    name = models.CharField(max_length=250)
    slug = models.SlugField(max_length=255, unique=True)
    categorie = models.ForeignKey(Categories, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Produits"


class Condition(models.Model):
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name


class Stockes(models.Model):
    produit = models.ForeignKey(Produits, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField(default=0)
    prix_achat = models.PositiveIntegerField(default=0)
    stock_minimum = models.PositiveIntegerField(default=5, help_text="Quantité minimale avant alerte")
    achat_ligne = models.ForeignKey('AchatLigne', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-achat_ligne__date_ajout']
        verbose_name_plural = "Stockes"
        unique_together = ('produit', 'achat_ligne')

    def __str__(self):
        lot = self.achat_ligne.lot if self.achat_ligne else '-'
        exp = self.achat_ligne.date_expiration if self.achat_ligne else '-'
        return f"{self.produit} | Lot: {lot} | Exp: {exp}"

    @property
    def lot(self):
        return self.achat_ligne.lot if self.achat_ligne else None

    @property
    def date_expiration(self):
        return self.achat_ligne.date_expiration if self.achat_ligne else None

    
    @property
    def description(self):
        return self.achat_ligne.description if self.achat_ligne else None

    @property
    def conditionnement(self):
        return self.achat_ligne.conditionnement if self.achat_ligne else None

    @property
    def date_ajout(self):
        return self.achat_ligne.date_ajout if self.achat_ligne else None
    @property
    def statut_quantite(self):
        if self.quantite > self.stock_minimum:
            return 'green'
        elif self.quantite > 0:
            return 'orange'
        else:
            return 'red'
    @property
    def est_expire(self):
        """Retourne True si le stock est expiré."""
        if self.date_expiration:
            return self.date_expiration < timezone.now().date()
        return False

    @property
    def statut_expiration(self):
        return "expiré" if self.est_expire else "valide"


class Customer(models.Model):
    name = models.CharField(max_length=100)
    NIF = models.CharField(max_length=100)
    phone = models.CharField(max_length=132, blank=True)
    address = models.CharField(max_length=64, default='', blank=True)
    created_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    save_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True)

    def __str__(self):
        return self.name






class Vente(models.Model):
    PAYMENT_STATUS_CASH = 'C'
    PAYMENT_STATUS_DETTE = 'D'
    PAYMENT_STATUS_CHEQUE = 'CH'
    PAYMENT_STATUS_ORDRE_DE_VIREMENT='OV'
    PAYMENT_STATUS_PAYER = 'P'
    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_STATUS_CASH, 'Cash'),
        (PAYMENT_STATUS_DETTE, 'Dette'),
        (PAYMENT_STATUS_CHEQUE, 'Cheque'),
        (PAYMENT_STATUS_PAYER, 'Payer'),
        (PAYMENT_STATUS_ORDRE_DE_VIREMENT, 'OV')
    ]

    date_vente = models.DateTimeField(default=timezone.now)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    statupaiement = models.CharField(max_length=50, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_STATUS_CASH)
    vendeur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='ventes_effectuees', null=True, blank=True)
    date_payement = models.DateTimeField(null=True, blank=True)
    annule = models.BooleanField(default=False, verbose_name="Annulée")
    numero_facture = models.CharField(max_length=20, unique=True, blank=True, null=True, verbose_name="Numéro de facture")

    def clean(self):
        # Vérifier la logique de date_payement
        if self.statupaiement in [self.PAYMENT_STATUS_CASH, self.PAYMENT_STATUS_CHEQUE]:
        # Si le statut est Cash ou Chèque, la date de paiement doit être aujourd'hui
            if self.date_payement and self.date_payement.date() != now().date():
                raise ValidationError("Pour un paiement en Cash ou Chèque, la date de paiement doit être aujourd'hui.")
        elif self.statupaiement in  [self.PAYMENT_STATUS_DETTE, self.PAYMENT_STATUS_ORDRE_DE_VIREMENT]:
            # Si le statut est Dette, la date de paiement doit être dans le futur
            if self.date_payement and self.date_payement.date() <= now().date():
                raise ValidationError("Pour un paiement en Dette ou OV, la date de paiement doit être supérieure à la date du jour.")

    def save(self, *args, validate=True, **kwargs):
        if validate:
            self.clean()
        if not self.numero_facture:
            # Cherche le plus grand numéro existant
            last_num = 0
            factures = Vente.objects.filter(numero_facture__startswith='FAC-')
            for v in factures:
                match = re.match(r'FAC-(\d+)', v.numero_facture or '')
                if match:
                    num = int(match.group(1))
                    if num > last_num:
                        last_num = num
            self.numero_facture = f"FAC-{last_num + 1:05d}"
        super().save(*args, **kwargs)

    def get_total_amount(self):
        total = sum(item.total_price for item in self.lignes.all())
        return total

    def __str__(self):
        return f"Vente {self.id} - {self.customer.name}"


class VenteProduit(models.Model):
    vente = models.ForeignKey(Vente, related_name='lignes', on_delete=models.CASCADE)
    produit = models.ForeignKey(Stockes, on_delete=models.PROTECT)
    quantite = models.PositiveIntegerField(default=1)
    prix_vente = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    @property
    def total_price(self):
        return self.prix_vente * self.quantite

    def clean(self):
        if self.quantite > self.produit.quantite:
            raise ValidationError(f"Stock insuffisant. Disponible : {self.produit.quantite}")
    
    def save(self, *args, **kwargs): # Note: This save method is called from AddinvoiceView
        self.clean()
        is_new = self._state.adding

        if not is_new:
            # Updating a sale line is complex. For now, we assume it's not happening.
            # If it were, we'd need to revert the old stock change and apply the new one.
            super().save(*args, **kwargs)
            return

        with transaction.atomic():
            # Lock the stock item to prevent race conditions.
            stock_item = Stockes.objects.select_for_update().get(pk=self.produit.pk)

            quantite_avant = stock_item.quantite
            quantite_apres = stock_item.quantite - self.quantite

            # Save the sale line itself
            super().save(*args, **kwargs)

            # Update stock quantity
            stock_item.quantite = quantite_apres
            stock_item.save()

            # Create the tracking record and link it to this sale line
            ModificationStock.objects.create(
                produit=stock_item,
                type_modification='SORTIE',
                motif='VENTE',
                quantite=self.quantite,
                utilisateur=self.vente.vendeur,
                raison=f"Vente n°{self.vente.numero_facture}",
                quantite_avant=quantite_avant,
                quantite_apres=quantite_apres,
                vente_ligne=self
            )

    def __str__(self):
        return f"{self.produit.produit.name} - Quantité: {self.quantite} dans Vente {self.vente.id}"


class ModificationStock(models.Model):
    """Suivi des modifications de stock (entrées et sorties)"""
    TYPE_CHOICES = [
        ('ENTREE', 'Entrée en stock'),
        ('SORTIE', 'Sortie de stock'),
    ]

    MOTIF_CHOICES = [
        # Motifs d'entrée
        ('ACHAT', 'Achat fournisseur'),
        ('RETOUR_CLIENT', 'Entrée - Retour client'),
        ('AJUSTEMENT_POSITIF', "Entrée - Ajustement d'inventaire"),
        ('ANNULATION_VENTE', 'Entrée - Annulation de vente'),
        # Motifs de sortie
        ('VENTE', 'Vente client'),
        ('PERTE_PEREMPTION', 'Sortie - Perte (Péremption)'),
        ('PERTE_CASSE', 'Sortie - Perte (Casse)'),
        ('PERTE_VOL', 'Sortie - Perte (Vol)'),
        ('AJUSTEMENT_NEGATIF', "Sortie - Ajustement d'inventaire"),
        ('ANNULATION_ACHAT', "Sortie - Annulation d'achat"),
    ]
    
    produit = models.ForeignKey('Stockes', on_delete=models.CASCADE, related_name='modifications')
    type_modification = models.CharField(max_length=10, choices=TYPE_CHOICES)
    motif = models.CharField(max_length=30, choices=MOTIF_CHOICES, default='VENTE')
    quantite = models.PositiveIntegerField()
    quantite_avant = models.PositiveIntegerField(null=True, blank=True, help_text="Quantité en stock avant la modification")
    quantite_apres = models.PositiveIntegerField(null=True, blank=True, help_text="Quantité en stock après la modification")
    date_modification = models.DateTimeField(auto_now_add=True)
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='modifications_stock')
    raison = models.CharField(max_length=255, blank=True, null=True, help_text="Détails supplémentaires (ex: N° de vente/achat)")
    vente_ligne = models.OneToOneField(VenteProduit, on_delete=models.SET_NULL, null=True, blank=True, related_name='modification')
  
    def __str__(self):
        return f"{self.get_type_modification_display()} de {self.quantite} ({self.get_motif_display()}) - {self.produit.produit.name}"
    
    class Meta:
        verbose_name = "Modification de stock"
        verbose_name_plural = "Modifications de stock"
        ordering = ['-date_modification']
        

class Fournisseur(models.Model):
    nom = models.CharField(max_length=100)
    contact = models.CharField(max_length=100, blank=True)
    adresse = models.CharField(max_length=255, blank=True)
    # ...

    def __str__(self):
        return self.nom

class Achat(models.Model):
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.PROTECT)
    date_achat = models.DateTimeField(default=timezone.now)
    facture = models.CharField(max_length=100, blank=True)
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='achats_effectues')
    annule = models.BooleanField(default=False, verbose_name="Annulé")

    def __str__(self):
        return f"Achat {self.id} - {self.fournisseur.nom} ({self.date_achat.date()})"

    def get_total(self):
        return sum(ligne.get_total for ligne in self.lignes.all())

class AchatLigne(models.Model):
    achat = models.ForeignKey(Achat, related_name='lignes', on_delete=models.CASCADE)
    produit = models.ForeignKey(Produits, on_delete=models.PROTECT)
    quantite = models.PositiveIntegerField()
    prix_achat = models.DecimalField(max_digits=10, decimal_places=2)
    lot = models.CharField(max_length=250, blank=True, null=True)
    date_expiration = models.DateField(blank=True, null=True)
    conditionnement = models.ForeignKey(Condition, on_delete=models.CASCADE, default=1)  # Utilise l'ID 1 comme valeur par défaut
    date_ajout = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.produit.name} x{self.quantite} (Lot: {self.lot})"

    @property
    def get_total(self):
        return self.quantite * self.prix_achat

    class Meta:
        ordering = ['-date_ajout']
