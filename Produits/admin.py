from django.contrib import admin
from .models import Categories, Produits, Condition, Stockes, Customer, Vente, VenteProduit, Utilisateur
from django.utils.html import format_html

# Classe Admin pour Stockes
class StockesAdmin(admin.ModelAdmin):
    list_display = ('produit', 'price', 'condisionnement', 'quantite', 'statut_quantite_colored', 'description', 'date_ajout')
    search_fields = ['produit__name', 'description']
    
    date_hierarchy = 'date_ajout'
    list_per_page = 20
    
    def statut_quantite_colored(self, obj):
        """Afficher le statut de quantité avec une couleur correspondante"""
        colors = {
            'red': '#FF0000',
            'orange': '#FFA500',
            'green': '#00FF00'
        }
        status = obj.statut_quantite()
        return format_html(
            '<span style="color: {};">{}</span>',
            colors[status],
            status.upper()
        )
    
    statut_quantite_colored.short_description = 'Statut'

# Classe Admin pour Customer
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'phone', 'address', 'created_date', 'save_by')
    search_fields = ['name', 'email', 'phone']
    list_filter = ('created_date', 'save_by')
    date_hierarchy = 'created_date'

# Classe Inline pour VenteProduit
class VenteProduitInline(admin.TabularInline):
    model = VenteProduit
    extra = 1
    autocomplete_fields = ['produit']
    
    # Ajout des champs readonly pour afficher les informations calculées
    readonly_fields = ['prix_unitaire', 'prix_total']
    
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
    list_display = ('id', 'customer', 'date_vente', 'statut_paiement_display', 'montant_total')
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
# Enregistrement des autres modèles avec leurs classes Admin respectives
admin.site.register(Stockes, StockesAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Vente, VenteAdmin)

