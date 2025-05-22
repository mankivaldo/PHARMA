from django.urls import path
from django.contrib.auth.views import LogoutView
from django.contrib.auth.decorators import login_required
from .views import (
    produit_list, produit_detail, produit_form,
    add_produit, Affichage, update_données,
    MyModelDeleteView, edit, detail_vente,
    AddinvoiceView, ListeVentesView,
    liste_utilisateurs, creer_utilisateur, modifier_utilisateur, supprimer_utilisateur,
    connexion, inscription,
    liste_conditions, ajouter_condition, modifier_condition, supprimer_condition,
    liste_customers, ajouter_customer, modifier_customer, supprimer_customer,
    liste_categories, ajouter_categorie, modifier_categorie, supprimer_categorie,
    export_ventes_excel
)

urlpatterns = [
    # Pages d'authentification
    path('connexion/', connexion, name='connexion'),
    path('inscription/', inscription, name='inscription'),
    path('logout/', LogoutView.as_view(next_page='connexion'), name='logout'),
    
    # Pages protégées
    path('', login_required(Affichage.as_view(), login_url='connexion'), name='home'),
    path('add-produit/', login_required(add_produit.as_view(), login_url='connexion'), name='add-produit'),
    path('vente/', login_required(AddinvoiceView.as_view(), login_url='connexion'), name='vente'),
    path('modifier/<int:pk>/', login_required(update_données.as_view(), login_url='connexion'), name='modifier'),
    path('detail/<int:pk>/', login_required(edit.as_view(), login_url='connexion'), name='detail'),
    path('delete/<int:pk>/', login_required(MyModelDeleteView.as_view(), login_url='connexion'), name='delete'),
    path('detail-vente/<int:pk>/', login_required(detail_vente.as_view(), login_url='connexion'), name='detail-vente'),
    path('liste-ventes/', login_required(ListeVentesView.as_view(), login_url='connexion'), name='liste_ventes'),
    path('produit/nouveau/', login_required(produit_form), name='produit_nouveau'),
    path('produits/', login_required(produit_list), name='produit_list'),
    path('produit/<str:name>/edit/', login_required(produit_form), name='produit_form'),
    path('produit/<str:name>/', login_required(produit_detail), name='produit_detail'),
    
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
    path('export-ventes-excel/', export_ventes_excel, name='export_ventes_excel'),
]