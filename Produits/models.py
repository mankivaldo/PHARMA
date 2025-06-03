from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from django.utils import timezone 
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.hashers import make_password, check_password

class Categories(models.Model):
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"


class Produits(models.Model):
    name = models.CharField(max_length=250)
    categorie = models.ForeignKey(Categories, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Produits"


class Condition(models.Model):
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name


class Stockes(models.Model):
    produit = models.ForeignKey(Produits, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField(default=0)
    prix_vente = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
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
    def prix_achat(self):
        return self.achat_ligne.prix_achat if self.achat_ligne else None

    @property
    def description(self):
        return self.achat_ligne.description if self.achat_ligne else None

    @property
    def conditionnement(self):
        return self.achat_ligne.conditionnement if self.achat_ligne else None

    @property
    def date_ajout(self):
        return self.achat_ligne.date_ajout if self.achat_ligne else None


class Customer(models.Model):
    name = models.CharField(max_length=100)
    NIF = models.CharField(max_length=100)
    phone = models.CharField(max_length=132, null=True, blank=True)
    address = models.CharField(max_length=64, default='')
    created_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    save_by = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)

    def __str__(self):
        return self.name






class Vente(models.Model):
    PAYMENT_STATUS_CASH = 'C'
    PAYMENT_STATUS_DETTE = 'D'
    PAYMENT_STATUS_CHEQUE = 'CH'
    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_STATUS_CASH, 'Cash'),
        (PAYMENT_STATUS_DETTE, 'Dette'),
        (PAYMENT_STATUS_CHEQUE, 'Cheque')
    ]

    date_vente = models.DateTimeField(default=timezone.now)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    statupaiement = models.CharField(max_length=50, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_STATUS_CASH)
    vendeur = models.ForeignKey(User, on_delete=models.PROTECT, related_name='ventes_effectuees', null=True, blank=True)
    date_payement = models.DateTimeField(null=True, blank=True)

    def clean(self):
        # Vérifier la logique de date_payement
        if self.statupaiement in [self.PAYMENT_STATUS_CASH, self.PAYMENT_STATUS_CHEQUE]:
            # Si le statut est Cash ou Chèque, la date de paiement doit être aujourd'hui
            if self.date_payement and self.date_payement.date() != now().date():
                raise ValidationError("Pour un paiement en Cash ou Chèque, la date de paiement doit être aujourd'hui.")
        elif self.statupaiement == self.PAYMENT_STATUS_DETTE:
            # Si le statut est Dette, la date de paiement doit être dans le futur
            if self.date_payement and self.date_payement.date() <= now().date():
                raise ValidationError("Pour un paiement en Dette, la date de paiement doit être supérieure à la date du jour.")

    def save(self, *args, **kwargs):
        # Appeler la méthode clean avant de sauvegarder
        self.clean()
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
    
    def save(self, *args, **kwargs):
        self.clean()
        is_new = self._state.adding
        super().save(*args, **kwargs)
        # Mise à jour de la quantité en stock
        self.produit.quantite -= self.quantite
        self.produit.save()
        # Traçabilité du mouvement (uniquement à la création)
        if is_new:
            ModificationStock.objects.create(
                produit=self.produit,
                type_modification='SORTIE',
                quantite=self.quantite,
                utilisateur=self.vente.vendeur,
                raison=f"Vente n°{self.vente.id}"
            )

    def __str__(self):
        return f"{self.produit.produit.name} - Quantité: {self.quantite} dans Vente {self.vente.id}"


class ModificationStock(models.Model):
    """Suivi des modifications de stock (entrées et sorties)"""
    TYPE_CHOICES = [
        ('ENTREE', 'Entrée en stock'),
        ('SORTIE', 'Sortie de stock'),
        ('AJUSTEMENT', 'Ajustement d\'inventaire'),
    ]
    
    produit = models.ForeignKey('Stockes', on_delete=models.CASCADE, related_name='modifications')
    type_modification = models.CharField(max_length=10, choices=TYPE_CHOICES)
    quantite = models.PositiveIntegerField()
    date_modification = models.DateTimeField(auto_now_add=True)
    utilisateur = models.ForeignKey(User, on_delete=models.PROTECT, related_name='modifications_stock')
    raison = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return f"{self.get_type_modification_display()} - {self.produit.produit.name} ({self.quantite})"
    
    class Meta:
        verbose_name = "Modification de stock"
        verbose_name_plural = "Modifications de stock"
        ordering = ['-date_modification']
        

class Utilisateur(models.Model):
    utilisateur = models.CharField(max_length=250)
    email = models.EmailField(max_length=250)
    mot_de_passe = models.CharField(max_length=250)
   
    def __str__(self):
        return self.utilisateur

    def set_password(self, raw_password):
        """Hash et stocke le mot de passe"""
        self.mot_de_passe = make_password(raw_password)
        self.save()

    def check_password(self, raw_password):
        """Vérifie si le mot de passe fourni correspond au hash stocké"""
        return check_password(raw_password, self.mot_de_passe)

    def save(self, *args, **kwargs):
    # Pour un nouvel utilisateur
        if self._state.adding:
            self.mot_de_passe = make_password(self.mot_de_passe)
        else:
            # Pour une modification
            try:
                ancien = Utilisateur.objects.get(pk=self.pk)
                # Vérifier si le mot de passe a été modifié
                if self.mot_de_passe != ancien.mot_de_passe:
                    # S'il a été modifié, le hasher
                    self.mot_de_passe = make_password(self.mot_de_passe)
            except Utilisateur.DoesNotExist:
                # Sécurité supplémentaire
                self.mot_de_passe = make_password(self.mot_de_passe)
        
        # Sauvegarde finale
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"


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
    utilisateur = models.ForeignKey(User, on_delete=models.PROTECT)
    # ...

    def __str__(self):
        return f"Achat {self.id} - {self.fournisseur.nom} ({self.date_achat.date()})"

class AchatLigne(models.Model):
    achat = models.ForeignKey(Achat, related_name='lignes', on_delete=models.CASCADE)
    produit = models.ForeignKey(Produits, on_delete=models.PROTECT)
    quantite = models.PositiveIntegerField()
    prix_achat = models.DecimalField(max_digits=10, decimal_places=2)
    lot = models.CharField(max_length=250, blank=True, null=True)
    date_expiration = models.DateField(blank=True, null=True)
    conditionnement = models.ForeignKey(Condition, on_delete=models.CASCADE, default=1)  # Utilise l'ID 1 comme valeur par défaut
    description = models.TextField(blank=True)
    date_ajout = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.produit.name} x{self.quantite} (Lot: {self.lot})"

    class Meta:
        ordering = ['-date_ajout']

