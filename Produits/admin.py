from django.contrib import admin
from .models import Categories, Produits, Condition, Stockes, Customer, Vente, VenteProduit, Utilisateur, ModificationStock, Fournisseur, Achat, AchatLigne
from django.utils.html import format_html

# Classe Admin pour Stockes
class StockesAdmin(admin.ModelAdmin):
    list_display = ('produit', 'get_lot', 'get_prix_achat', 'prix_vente', 'get_conditionnement', 'quantite', 
                   'stock_status_colored', 'get_date_expiration', 'get_date_ajout')
    list_filter = ('achat_ligne__conditionnement', 'achat_ligne__date_ajout')
    search_fields = ['produit__name', 'achat_ligne__description', 'achat_ligne__lot']
    readonly_fields = ['get_date_ajout']
    date_hierarchy = 'achat_ligne__date_ajout'
    list_per_page = 20
    
    fieldsets = (
        ('Informations principales', {
            'fields': ('produit', 'quantite', 'stock_minimum')
        }),
        ('Prix', {
            'fields': ('prix_vente', 'achat_ligne'),
        })
    )

    def get_lot(self, obj):
        return obj.lot
    get_lot.short_description = 'Lot'
    get_lot.admin_order_field = 'achat_ligne__lot'

    def get_prix_achat(self, obj):
        return obj.prix_achat
    get_prix_achat.short_description = 'Prix d\'achat'
    get_prix_achat.admin_order_field = 'achat_ligne__prix_achat'

    def get_conditionnement(self, obj):
        return obj.conditionnement
    get_conditionnement.short_description = 'Conditionnement'
    get_conditionnement.admin_order_field = 'achat_ligne__conditionnement'

    def get_date_expiration(self, obj):
        return obj.date_expiration
    get_date_expiration.short_description = 'Date d\'expiration'
    get_date_expiration.admin_order_field = 'achat_ligne__date_expiration'

    def get_date_ajout(self, obj):
        return obj.date_ajout
    get_date_ajout.short_description = 'Date d\'ajout'
    get_date_ajout.admin_order_field = 'achat_ligne__date_ajout'

    def stock_status_colored(self, obj):
        """Afficher le statut de stock avec une couleur selon le niveau"""
        if obj.quantite == 0:
            color = '#FF0000'  # Rouge pour stock épuisé
            status = 'ÉPUISÉ'
        elif obj.quantite < obj.stock_minimum:
            color = '#FFA500'  # Orange pour stock bas
            status = 'BAS'
        else:
            color = '#00FF00'  # Vert pour stock ok
            status = 'OK'

        return format_html(
            '<span style="color: {};"><b>{}</b> ({})</span>',
            color,
            status,
            obj.quantite
        )
    stock_status_colored.short_description = 'Niveau de stock'

# Classe Admin pour Customer
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'NIF', 'phone', 'address', 'created_date', 'save_by')
    search_fields = ['name', 'NIF', 'phone']
    list_filter = ('created_date', 'save_by')
    date_hierarchy = 'created_date'

# Classe Inline pour VenteProduit
class VenteProduitInline(admin.TabularInline):
    model = VenteProduit
    extra = 1
    autocomplete_fields = ['produit']
    
    # Ajout des champs readonly pour afficher les informations calculées
    readonly_fields = [ 'prix_total']
    
    def prix_unitaire(self, obj):
        if obj.produit_id:
            return obj.produit.price
        return 0
    
    def prix_total(self, obj):
        if hasattr(obj, 'total_price'):
            return obj.total_price
        if obj.produit_id:
            return obj.produit.price * obj.quantite
        return 0
    prix_unitaire.short_description = 'Prix unitaire'
    prix_total.short_description = 'Prix total'
    

    

# Classe Admin pour Vente
class VenteAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'date_vente', 'statut_paiement_display', 'montant_total', 'vendeur', 'date_payement')
    list_filter = ('date_vente', 'statupaiement')
    search_fields = ['customer__name', 'id']
    date_hierarchy = 'date_vente'
    inlines = [VenteProduitInline]
    
    def statut_paiement_display(self, obj):
        statuts = {
            'C': 'Comptant',
            'D': 'Dette',
            'CH': 'Chèque'
        }
        return statuts.get(obj.statupaiement, obj.statupaiement)
    
    def montant_total(self, obj):
        return obj.get_total_amount()
    
    statut_paiement_display.short_description = 'Statut de paiement'
    montant_total.short_description = 'Montant total'

# Enregistrement des modèles
@admin.register(Categories)
class CategoriesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ['name']

@admin.register(Produits)
class ProduitsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name','categorie')
    search_fields = ['name']

@admin.register(Condition)
class ConditionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ['name']
@admin.register(Utilisateur)
class UtilisateurAdmin(admin.ModelAdmin):
    list_display = ('id', 'utilisateur', 'email', 'mot_de_passe')
    search_fields = ['utilisateur', 'email']

# Classe Inline pour AchatLigne
class AchatLigneInline(admin.TabularInline):
    model = AchatLigne
    extra = 1
    autocomplete_fields = ['produit']

# Classe Admin pour Fournisseur
@admin.register(Fournisseur)
class FournisseurAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom', 'contact', 'adresse')
    search_fields = ['nom', 'contact']
    list_filter = ['nom']

# Classe Admin pour Achat
@admin.register(Achat)
class AchatAdmin(admin.ModelAdmin):
    list_display = ('id', 'fournisseur', 'date_achat', 'facture', 'utilisateur')
    list_filter = ('date_achat', 'fournisseur')
    search_fields = ['facture', 'fournisseur__nom']
    date_hierarchy = 'date_achat'
    inlines = [AchatLigneInline]

# Classe Admin pour ModificationStock
@admin.register(ModificationStock)
class ModificationStockAdmin(admin.ModelAdmin):
    list_display = ('id', 'produit', 'type_modification', 'quantite', 'date_modification', 'utilisateur', 'raison')
    list_filter = ('type_modification', 'date_modification', 'utilisateur')
    search_fields = ['produit__produit__name', 'raison']
    date_hierarchy = 'date_modification'

# Enregistrement des autres modèles avec leurs classes Admin respectives
admin.site.register(Stockes, StockesAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Vente, VenteAdmin)

