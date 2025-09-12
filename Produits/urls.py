from django.urls import path
from django.contrib.auth.views import LogoutView
from django.contrib.auth.decorators import login_required
from .views import *
from .views_entreprise import *


urlpatterns = [
    # Pages d'authentification
    path('connexion/', connexion, name='connexion'),
    path('inscription/', inscription, name='inscription'),
    path('logout/', LogoutView.as_view(next_page='connexion'), name='logout'),
    # Pages protégées
    path('', login_required(DashboardView.as_view(), login_url='connexion'), name='home'),
    path('vente/', login_required(AddinvoiceView.as_view(), login_url='connexion'), name='vente'),
    path('detail-vente/<int:pk>/', login_required(detail_vente.as_view(), login_url='connexion'), name='detail-vente'),
    path('liste-ventes/', login_required(ListeVentesView.as_view(), login_url='connexion'), name='liste_ventes'),
    path('produit/nouveau/', login_required(produit_form), name='produit_nouveau'),
    path('produits/', login_required(produit_list), name='produit_list'),
    path('produit/<slug:slug>/edit/', login_required(produit_form), name='produit_form'),
    path('produit/<slug:slug>/', login_required(produit_detail), name='produit_detail'),
    
    # Gestion des utilisateurs
    path('utilisateurs/', login_required(liste_utilisateurs), name='liste_utilisateurs'),
    path('utilisateur/nouveau/', login_required(creer_utilisateur), name='creer_utilisateur'),
    path('utilisateur/<int:pk>/modifier/', login_required(modifier_utilisateur), name='modifier_utilisateur'),
    path('utilisateur/<int:pk>/supprimer/', login_required(supprimer_utilisateur), name='supprimer_utilisateur'),

    # URLs pour les conditions
    path('conditions/', login_required(liste_conditions), name='liste_conditions'),
    path('condition/ajouter/', login_required(ajouter_condition), name='ajouter_condition'),
    path('condition/<int:pk>/modifier/', login_required(modifier_condition), name='modifier_condition'),
    path('condition/<int:pk>/supprimer/', login_required(supprimer_condition), name='supprimer_condition'),

    # URLs pour les clients
    path('clients/', login_required(liste_customers), name='liste_customers'),
    path('client/ajouter/', login_required(ajouter_customer), name='ajouter_customer'),
    path('client/<int:pk>/modifier/', login_required(modifier_customer), name='modifier_customer'),
    path('client/<int:pk>/supprimer/', login_required(supprimer_customer), name='supprimer_customer'),

    # URLs pour les catégories
    path('categories/', login_required(liste_categories), name='liste_categories'),
    path('categorie/ajouter/', login_required(ajouter_categorie), name='ajouter_categorie'),
    path('categorie/<int:pk>/modifier/', login_required(modifier_categorie), name='modifier_categorie'),
    path('categorie/<int:pk>/supprimer/', login_required(supprimer_categorie), name='supprimer_categorie'),

    # Export ventes
    path('export-ventes-excel/', export_ventes_excel, name='export_ventes_excel'),    # Gestion des achats
    path('achats/', login_required(ListeAchatsView.as_view(), login_url='connexion'), name='liste_achats'),
    path('achats/ajouter/', login_required(ajouter_achat, login_url='connexion'), name='ajouter_achat'),
    path('achat/<int:pk>/', login_required(DetailAchatView.as_view(), login_url='connexion'), name='detail_achat'),

    # Gestion des stocks
    path('stocks/', login_required(ListeStockView.as_view()), name='liste_stock'),
    path('stock/ajuster/', login_required(ajuster_stock), name='ajuster_stock'),
   
    # URLs pour les fournisseurs
    path('fournisseurs/', login_required(liste_fournisseurs), name='liste_fournisseurs'),
    path('fournisseur/ajouter/', login_required(ajouter_fournisseur), name='ajouter_fournisseur'),
    path('fournisseur/<int:pk>/modifier/', login_required(modifier_fournisseur), name='modifier_fournisseur'),
    path('fournisseur/<int:pk>/supprimer/', login_required(supprimer_fournisseur), name='supprimer_fournisseur'),

    # Annuler vente et achat
    path('vente/<int:pk>/annuler/', login_required(annuler_vente), name='annuler_vente'),
    path('achat/<int:pk>/annuler/', login_required(annuler_achat), name='annuler_achat'),

    # Facture vente

    path('vente/<int:pk>/marquer_payee/', login_required(marquer_vente_payee), name='marquer_vente_payee'),

    path('facture-vente/<int:pk>/', login_required(facture_vente_view), name='facture_vente'),

    # Gestion des entreprises
    path('entreprises/', login_required(liste_entreprises), name='liste_entreprises'),
    path('entreprise/ajouter/', login_required(ajouter_entreprise), name='ajouter_entreprise'),
    path('entreprise/<int:pk>/modifier/', login_required(modifier_entreprise), name='modifier_entreprise'),
    path('entreprise/<int:pk>/supprimer/', login_required(supprimer_entreprise), name='supprimer_entreprise'),
    
    
    # Historique des ventes
    path('historique-ventes/', login_required(historique_ventes), name='historique_ventes'),
    
]