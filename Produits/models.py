from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
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
    price = models.DecimalField(max_digits=10, decimal_places=2)
    condisionnement = models.ForeignKey(Condition, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField(default=0)
    description = models.TextField()
    date_ajout = models.DateTimeField(default=timezone.now)
    date_expiration = models.DateField()

    class Meta:
        ordering = ['-date_ajout']
        verbose_name_plural = "Stockes"

    def statut_quantite(self):
        if self.quantite == 0:
            return 'red'
        elif self.quantite <= 10:
            return 'orange'
        else:
            return 'green'

    def __str__(self):
        return f"{self.produit}"


class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(null=True, blank=True)
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

    date_vente = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    statupaiement = models.CharField(max_length=50, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_STATUS_CASH)
    vendeur = models.ForeignKey(User, on_delete=models.PROTECT, related_name='ventes_effectuees', null=True, blank=True)

    def get_total_amount(self):
        total = sum(item.total_price for item in self.Ventes.all())
        return total

    def __str__(self):
        return f"Vente {self.id} - {self.customer.name}"


class VenteProduit(models.Model):
    vente = models.ForeignKey(Vente, related_name='Ventes', on_delete=models.CASCADE)
    produit = models.ForeignKey(Stockes, on_delete=models.PROTECT)
    quantite = models.PositiveIntegerField(default=1)

    @property
    def total_price(self):
        return self.produit.price * self.quantite

    def clean(self):
        if self.quantite > self.produit.quantite:
            raise ValidationError(f"Stock insuffisant. Disponible : {self.produit.quantite}")
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
        # Mise à jour de la quantité en stock
        self.produit.quantite -= self.quantite
        self.produit.save()

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
     
