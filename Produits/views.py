from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, View
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.contrib import messages
from datetime import datetime
from django.db import transaction
from django.utils import timezone
from django.core.paginator import Paginator
from .forms import *
from .models import *

# Fonctions de base pour la gestion des produits
@login_required
def produit_list(request):
    produits = Produits.objects.all()
    return render(request, 'produit_list.html', {'produits': produits})

@login_required
def produit_detail(request, name):
    produit = get_object_or_404(Produits, name=name)
    return render(request, 'produit_detail.html', {'produit': produit})

@login_required
def produit_form(request, name=None):
    if name:
        produit = get_object_or_404(Produits, name=name)
        form = ProduitForm(instance=produit)
    else:
        form = ProduitForm()
    
    if request.method == 'POST':
        if name:
            form = ProduitForm(request.POST, instance=produit)
        else:
            form = ProduitForm(request.POST)
            
        if form.is_valid():
            form.save()
            return redirect('produit_detail', name=form.instance.name)
    
    return render(request, 'produit_form.html', {'form': form})

# Class d'ajout des données
class add_produit(LoginRequiredMixin, View):
    template_name = 'add-Produits.html'
    form_class = AjoutProduits
    login_url = 'connexion'
    
    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            # Récupérer les données du formulaire
            produit = form.cleaned_data.get('produit')
            quantite = form.cleaned_data.get('quantite')
            price = form.cleaned_data.get('price')
            condisionnement = form.cleaned_data.get('condisionnement')
            date_expiration = form.cleaned_data.get('date_expiration')
            description = form.cleaned_data.get('description', '')
            
            # Vérifier si ce produit exact existe déjà
            try:
                stock = Stockes.objects.get(produit=produit)
                stock = Stockes.objects.get(date_expiration=date_expiration)
                # Si trouvé, mettre à jour la quantité, le prix et la date
                stock.quantite += quantite
                stock.price = price
                stock.date_ajout = timezone.now()
                stock.save()
                messages.success(request, "Stock du produit mis à jour avec succès!")
            except Stockes.DoesNotExist:
                # Le produit n'existe pas, créer un nouveau stock
                nouveau_stock = Stockes.objects.create(
                    produit=produit,
                    quantite=quantite,
                    price=price,
                    condisionnement=condisionnement,
                    description=description,
                    date_ajout=timezone.now(),
                    date_expiration=date_expiration
                )
                messages.success(request, "Nouveau produit ajouté avec succès!")
            except Stockes.MultipleObjectsReturned:
                # Gérer le cas où plusieurs stocks sont trouvés pour le même produit
                stock = Stockes.objects.filter(produit=produit).first()
                stock.quantite += quantite
                stock.price = price
                stock.date_ajout = timezone.now()
                stock.save()
                messages.success(request, "Stock mis à jour avec succès (plusieurs stocks trouvés)!")
            
            return redirect('home')
        
        return render(request, self.template_name, {'form': form})

# Generique fonction
class Affichage(LoginRequiredMixin, ListView):
    template_name = 'comptent.html'
    queryset = Stockes.objects.all()
    login_url = 'connexion'

# Classe pour la modification
class update_données(LoginRequiredMixin, UpdateView):
    model = Stockes
    form_class = AjoutProduits
    template_name = 'modification.html'
    success_url = reverse_lazy('home')
    login_url = 'connexion'

# Delete
class MyModelDeleteView(LoginRequiredMixin, DeleteView):
    model = Stockes
    template_name = 'comptent.html'
    success_url = reverse_lazy('home')
    login_url = 'connexion'

# Fonction de voir detail
class edit(LoginRequiredMixin, DetailView):
    model = Stockes
    template_name = "detail.html"
    login_url = 'connexion'

# List view
class detail_vente(LoginRequiredMixin, DetailView):
    model = Vente
    template_name = "detail_vente.html"
    context_object_name = "vente"
    login_url = 'connexion'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['produits_vendus'] = VenteProduit.objects.filter(vente=self.object)
        return context

# Fonction pour vente
class AddinvoiceView(LoginRequiredMixin, View):
    template_name = "vente.html"
    login_url = 'connexion'
    
    def get(self, request, *args, **kwargs):
        customers = Customer.objects.select_related('save_by').all()
        stocks = Stockes.objects.filter(quantite__gt=0)
        
        context = {
            'Customers': customers,
            'Stocks': stocks
        }
        
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        customers = Customer.objects.select_related('save_by').all()
        stocks = Stockes.objects.filter(quantite__gt=0)
        
        context = {
            'Customers': customers,
            'Stocks': stocks
        }
        
        if request.method == 'POST':
            client_id = request.POST.get('client')
            payment_type = request.POST.get('payment')
            
            if client_id:
                customer = get_object_or_404(Customer, id=client_id)
                
                vente = Vente.objects.create(
                    customer=customer,
                    statupaiement=payment_type
                )
                
                stocks = request.POST.getlist('stock[]')
                quantities = request.POST.getlist('qt[]')
                
                for i in range(len(stocks)):
                    if i < len(quantities):
                        stock_id = stocks[i]
                        quantity = int(quantities[i])
                        
                        if stock_id and quantity > 0:
                            stock = get_object_or_404(Stockes, id=stock_id)
                            
                            if stock.quantite >= quantity:
                                VenteProduit.objects.create(
                                    vente=vente,
                                    produit=stock,
                                    quantite=quantity
                                )
                            else:
                                messages.error(request, f"Stock insuffisant pour {stock.produit.name}")
                
                messages.success(request, "Vente enregistrée avec succès!")
                return redirect('home')
            else:
                messages.error(request, "Veuillez sélectionner un client")
        
        return render(request, self.template_name, context)

class ListeVentesView(LoginRequiredMixin, ListView):
    model = Vente
    template_name = "liste_ventes.html"
    context_object_name = "ventes"
    login_url = 'connexion'
    ordering = ['-date_vente']
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        date_debut = self.request.GET.get('date_debut')
        date_fin = self.request.GET.get('date_fin')
        client_id = self.request.GET.get('client')
        statut = self.request.GET.get('statut')
        
        if date_debut:
            queryset = queryset.filter(date_vente__gte=date_debut)
        
        if date_fin:
            queryset = queryset.filter(date_vente__lte=date_fin + ' 23:59:59')
        
        if client_id:
            queryset = queryset.filter(customer_id=client_id)
        
        if statut:
            queryset = queryset.filter(statupaiement=statut)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['clients'] = Customer.objects.all()
        
        total_ventes = self.get_queryset().count()
        montant_total = sum(vente.get_total_amount() for vente in self.get_queryset())
        
        context['total_ventes'] = total_ventes
        context['montant_total'] = montant_total
        
        return context


@login_required
def liste_utilisateurs(request):
    utilisateurs = Utilisateur.objects.all()
    print("Nombre d'utilisateurs:", utilisateurs.count())  # Pour déboguer
    for user in utilisateurs:
        print(user.utilisateur, user.email)  # Pour voir les données
    return render(request, 'user/liste_utilisateurs.html', {'utilisateurs': utilisateurs})


@login_required
def creer_utilisateur(request):
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"L'utilisateur {user.username} a été créé avec succès.")
            return redirect('liste_utilisateurs')
    else:
        form = InscriptionForm()
    
    return render(request, 'user/inscription.html', {'form': form})

@login_required
def modifier_utilisateur(request, pk):
    utilisateur = get_object_or_404(Utilisateur, pk=pk)
    utilisateurs = Utilisateur.objects.all().order_by('-id')
    
    if request.method == 'POST':
        form = InscriptionForm(request.POST, instance=utilisateur)
        if form.is_valid():
            utilisateur_modifie = form.save()
            print(f"Utilisateur modifié: {utilisateur_modifie.id} - {utilisateur_modifie.utilisateur}")  # Débogage
            messages.success(request, 'Utilisateur modifié avec succès')
            return redirect('liste_utilisateurs')  # Rediriger vers liste plutôt que création
    else:
        form = InscriptionForm(instance=utilisateur)
    
    return render(request, 'user/inscription.html', {
        'form': form,
        'utilisateurs': utilisateurs,
        'utilisateur_courant': utilisateur
    })

@login_required
def supprimer_utilisateur(request, pk):
    utilisateur = get_object_or_404(Utilisateur, pk=pk)
    if request.method == 'POST':
        utilisateur.delete()
        messages.success(request, 'Utilisateur supprimé avec succès')
        return redirect('creer_utilisateur')
    return redirect('creer_utilisateur')

def connexion(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Connexion réussie!')
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
            else:
                messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    else:
        form = LoginForm()
    return render(request, 'user/connexion.html', {'form': form})

def inscription(request):
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['mot_de_passe'])
            user.save()
            messages.success(request, 'Inscription réussie! Vous pouvez maintenant vous connecter.')
            return redirect('connexion')
    else:
        form = InscriptionForm()
    return render(request, 'user/inscription.html', {'form': form})

# Vues pour les catégories
@login_required
def liste_categories(request):
    categories = Categories.objects.all().order_by('-id')
    return render(request, 'categorie/liste_categories.html', {'categories': categories})

@login_required
def ajouter_categorie(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        if name:
            Categories.objects.create(name=name, description=description)
            messages.success(request, 'Catégorie ajoutée avec succès!')
            return redirect('liste_categories')
        else:
            messages.error(request, 'Le nom de la catégorie est requis')
    return render(request, 'categorie/ajouter_categorie.html')

@login_required
def modifier_categorie(request, pk):
    categorie = get_object_or_404(Categories, id=pk)
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            categorie.name = name
            categorie.save()
            messages.success(request, 'Catégorie modifiée avec succès!')
        else:
            messages.error(request, 'Le nom de la catégorie est requis')
    return redirect('liste_categories')

@login_required
def supprimer_categorie(request, pk):
    categorie = get_object_or_404(Categories, id=pk)
    try:
        categorie.delete()
        messages.success(request, 'Catégorie supprimée avec succès!')
    except:
        messages.error(request, 'Impossible de supprimer cette catégorie car elle est utilisée par des produits')
    return redirect('liste_categories')

# Vues pour les conditions
@login_required
def liste_conditions(request):
    conditions = Condition.objects.all().order_by('-id')
    return render(request, 'condition_list.html', {'conditions': conditions})

@login_required
def ajouter_condition(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Condition.objects.create(name=name)
            messages.success(request, 'Condition ajoutée avec succès!')
        else:
            messages.error(request, 'Le nom de la condition est requis')
    return redirect('liste_conditions')

@login_required
def modifier_condition(request, pk):
    condition = get_object_or_404(Condition, id=pk)
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            condition.name = name
            condition.save()
            messages.success(request, 'Condition modifiée avec succès!')
        else:
            messages.error(request, 'Le nom de la condition est requis')
    return redirect('liste_conditions')

@login_required
def supprimer_condition(request, pk):
    condition = get_object_or_404(Condition, id=pk)
    try:
        condition.delete()
        messages.success(request, 'Condition supprimée avec succès!')
    except:
        messages.error(request, 'Impossible de supprimer cette condition car elle est utilisée par des stocks')
    return redirect('liste_conditions')

# Vues pour les clients
@login_required
def liste_customers(request):
    customers = Customer.objects.all().order_by('-id')
    return render(request, 'customer_list.html', {'customers': customers})

@login_required
def ajouter_customer(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        address = request.POST.get('address')
        
        if name and phone:
            Customer.objects.create(
                name=name,
                phone=phone,
                email=email,
                address=address
            )
            messages.success(request, 'Client ajouté avec succès!')
        else:
            messages.error(request, 'Le nom et le téléphone sont requis')
    return redirect('liste_customers')

@login_required
def modifier_customer(request, pk):
    customer = get_object_or_404(Customer, id=pk)
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        address = request.POST.get('address')
        
        if name and phone:
            customer.name = name
            customer.phone = phone
            customer.email = email
            customer.address = address
            customer.save()
            messages.success(request, 'Client modifié avec succès!')
        else:
            messages.error(request, 'Le nom et le téléphone sont requis')
    return redirect('liste_customers')

@login_required
def supprimer_customer(request, pk):
    customer = get_object_or_404(Customer, id=pk)
    try:
        customer.delete()
        messages.success(request, 'Client supprimé avec succès!')
    except:
        messages.error(request, 'Impossible de supprimer ce client car il est associé à des ventes')
    return redirect('liste_customers')

  
