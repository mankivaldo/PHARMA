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
import openpyxl
from openpyxl.styles import Font, Alignment
from django.http import HttpResponse
from django.forms import inlineformset_factory, modelformset_factory
from decimal import Decimal
from django.db.models import Sum, F

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


# Generique fonction
class Affichage(LoginRequiredMixin, ListView):
    template_name = 'comptent.html'
    queryset = Stockes.objects.all()
    login_url = 'connexion'





# List view
class detail_vente(LoginRequiredMixin, DetailView):
    model = Vente
    template_name = "detail_vente.html"
    context_object_name = "vente"
    login_url = 'connexion'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['produits_vendus'] = self.object.lignes.all()
        return context

# Fonction pour vente
class AddinvoiceView(LoginRequiredMixin, View):
    template_name = "vente.html"
    login_url = 'connexion'

    def get(self, request, *args, **kwargs):
        vente_form = VenteForm()
        customers = Customer.objects.all()
        stocks = Stockes.objects.filter(quantite__gt=0)
        context = {
            'vente_form': vente_form,
            'Customers': customers,
            'Stocks': stocks,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        vente_form = VenteForm(request.POST)
        if vente_form.is_valid():
            with transaction.atomic():
                vente = vente_form.save(commit=False)
                vente.vendeur = request.user
                vente.save()

                stocks = request.POST.getlist('stock[]')
                qts = request.POST.getlist('qt[]')
                prixs = request.POST.getlist('prix[]')
                for stock_id, qt, prix in zip(stocks, qts, prixs):
                    if stock_id and qt and prix:
                        VenteProduit.objects.create(
                            vente=vente,
                            produit_id=stock_id,
                            quantite=int(qt),
                            prix_vente=float(prix)
                        )
            messages.success(request, "Vente enregistrée avec succès!")
            return redirect('liste_ventes')
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")

        customers = Customer.objects.all()
        stocks = Stockes.objects.filter(quantite__gt=0)
        context = {
            'vente_form': vente_form,
            'Customers': customers,
            'Stocks': stocks,
        }
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
        date_payement = self.request.GET.get('date_payement')
        
        if date_debut:
            queryset = queryset.filter(date_vente__gte=date_debut)
        
        if date_fin:
            queryset = queryset.filter(date_vente__lte=date_fin + ' 23:59:59')
        
        if client_id:
            queryset = queryset.filter(customer_id=client_id)
        
        if statut:
            queryset = queryset.filter(statupaiement=statut)
        if date_payement:
            queryset = queryset.filter(date_payement__date=date_payement)
        
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
        NIF = request.POST.get('NIF')
        address = request.POST.get('address')
        
        if name and phone:
            Customer.objects.create(
                name=name,
                phone=phone,
                NIF=NIF,
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
        NIF = request.POST.get('NIF')
        address = request.POST.get('address')
        
        if name and phone:
            customer.name = name
            customer.phone = phone
            customer.NIF = NIF
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

@login_required
def export_ventes_excel(request):
    # Récupérer les filtres depuis la requête
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    client_id = request.GET.get('client')
    statut = request.GET.get('statut')

    # Filtrer les ventes
    ventes = Vente.objects.all()
    if date_debut:
        ventes = ventes.filter(date_vente__gte=date_debut)
    if date_fin:
        ventes = ventes.filter(date_vente__lte=date_fin + ' 23:59:59')
    if client_id:
        ventes = ventes.filter(customer_id=client_id)
    if statut:
        ventes = ventes.filter(statupaiement=statut)

    if not ventes.exists():
        messages.error(request, "Aucune vente trouvée pour les critères sélectionnés.")
        return redirect('liste_ventes')

    # Créer un fichier Excel
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Rapport des Ventes"

    headers = ["ID Vente", "Client", "statut", "Date de Vente", "Date de payement", "Produit", "Quantité", "Prix Total"]
    for col_num, header in enumerate(headers, 1):
        cell = sheet.cell(row=1, column=col_num)
        cell.value = header
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")

    row_num = 2
    for vente in ventes:
        for produit_vendu in vente.lignes.all():  # <-- ici, on utilise 'lignes'
            sheet.cell(row=row_num, column=1).value = vente.id
            sheet.cell(row=row_num, column=2).value = vente.customer.name
            sheet.cell(row=row_num, column=3).value = vente.statupaiement
            sheet.cell(row=row_num, column=4).value = vente.date_vente.strftime('%Y-%m-%d')
            sheet.cell(row=row_num, column=5).value = vente.date_payement.strftime('%Y-%m-%d') if vente.date_payement else ""
            sheet.cell(row=row_num, column=6).value = produit_vendu.produit.produit.name
            sheet.cell(row=row_num, column=7).value = produit_vendu.quantite
            sheet.cell(row=row_num, column=8).value = produit_vendu.quantite * produit_vendu.prix_vente
            row_num += 1

    # Ajuster la largeur des colonnes
    for column in sheet.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            except:
                pass
        sheet.column_dimensions[column_letter].width = max_length + 2

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="rapport_ventes.xlsx"'
    workbook.save(response)
    return response


@login_required
def ajuster_stock(request):
    if request.method == 'POST':
        form = AjustementStockForm(request.POST)
        if form.is_valid():
            stock = form.cleaned_data['stock']
            nouvelle_quantite = form.cleaned_data['nouvelle_quantite']
            raison = form.cleaned_data['raison']
            utilisateur = request.user

            ancienne_quantite = stock.quantite
            if nouvelle_quantite != ancienne_quantite:
                # Mise à jour du stock
                stock.quantite = nouvelle_quantite
                stock.save()
                # Traçabilité
                ModificationStock.objects.create(
                    produit=stock,
                    type_modification='AJUSTEMENT',
                    quantite=abs(nouvelle_quantite - ancienne_quantite),
                    utilisateur=utilisateur,
                    raison=raison
                )
            return redirect('liste_stock')
    else:
        form = AjustementStockForm()
    return render(request, 'ajuster_stock.html', {'form': form})

@login_required
def ajouter_achat(request):
    AchatLigneFormSet = modelformset_factory(AchatLigne, form=AchatLigneForm, extra=3)
    if request.method == 'POST':
        achat_form = AchatForm(request.POST)
        formset = AchatLigneFormSet(request.POST, queryset=AchatLigne.objects.none())
        if achat_form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():  # Utiliser une transaction pour garantir l'intégrité des données
                    # Sauvegarder l'achat
                    achat = achat_form.save(commit=False)
                    achat.utilisateur = request.user
                    achat.save()

                    # Traiter les lignes d'achat
                    for form in formset:
                        if form.cleaned_data:  # Vérifier qu'il y a des données
                            # Créer la ligne d'achat
                            ligne = form.save(commit=False)
                            ligne.achat = achat
                            ligne.save()

                            # Créer une entrée dans le stock
                            stock = Stockes.objects.create(
                                produit=ligne.produit,
                                quantite=ligne.quantite,
                                prix_vente=ligne.prix_achat * Decimal('1.2'),  # Marge de 20%
                                stock_minimum=5,
                                achat_ligne=ligne
                            )

                            # Enregistrer la modification de stock
                            ModificationStock.objects.create(
                                produit=stock,
                                type_modification='ENTREE',
                                quantite=ligne.quantite,
                                utilisateur=request.user,
                                raison=f"Achat n°{achat.id} - Lot: {ligne.lot}"
                            )

                messages.success(request, "Achat enregistré et stock mis à jour avec succès !")
                return redirect('liste_achats')

            except Exception as e:
                messages.error(request, f"Erreur lors de l'enregistrement : {str(e)}")
        else:
            for form in formset:
                for field, errors in form.errors.items():
                    messages.error(request, f"Erreur : {errors[0]}")
            if achat_form.errors:
                for field, errors in achat_form.errors.items():
                    messages.error(request, f"Erreur : {errors[0]}")
    else:
        achat_form = AchatForm()
        formset = AchatLigneFormSet(queryset=AchatLigne.objects.none())

    return render(request, 'ajouter_achat.html', {
        'achat_form': achat_form,
        'formset': formset
    })

class ListeStockView(LoginRequiredMixin, ListView):
    model = Stockes
    template_name = 'liste_stock.html'
    context_object_name = 'stocks'
    login_url = 'connexion'
    ordering = ['-achat_ligne__date_ajout']  # Correction: utiliser le champ via la relation
    paginate_by = 20  # Optionnel, pour paginer

    def get_queryset(self):
        queryset = super().get_queryset()
        # Ajoute ici des filtres si besoin (par produit, lot, etc.)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ajoute ici d'autres infos utiles pour le template
        return context

class DetailStockView(LoginRequiredMixin, DetailView):
    model = Stockes
    template_name = 'detail_stock.html'
    context_object_name = 'stock'
    login_url = 'connexion'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ajoute ici l'historique des mouvements si besoin
        context['modifications'] = self.object.modifications.all().order_by('-date_modification')
        return context

# Vues pour les fournisseurs
@login_required
def liste_fournisseurs(request):
    fournisseurs = Fournisseur.objects.all().order_by('-id')
    return render(request, 'liste_fournisseurs.html', {'fournisseurs': fournisseurs})

@login_required
def ajouter_fournisseur(request):
    if request.method == 'POST':
        form = FournisseurForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fournisseur ajouté avec succès!')
            return redirect('liste_fournisseurs')
    else:
        form = FournisseurForm()
    return render(request, 'ajout_fourniseur.html', {'form': form})

@login_required
def modifier_fournisseur(request, pk):
    fournisseur = get_object_or_404(Fournisseur, pk=pk)
    if request.method == 'POST':
        form = FournisseurForm(request.POST, instance=fournisseur)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fournisseur modifié avec succès!')
            return redirect('liste_fournisseurs')
    else:
        form = FournisseurForm(instance=fournisseur)
    return render(request, 'ajout_fourniseur.html', {'form': form, 'fournisseur': fournisseur})

@login_required
def supprimer_fournisseur(request, pk):
    fournisseur = get_object_or_404(Fournisseur, pk=pk)
    try:
        fournisseur.delete()
        messages.success(request, 'Fournisseur supprimé avec succès!')
    except Exception as e:
        messages.error(request, 'Impossible de supprimer ce fournisseur car il est lié à des achats.')
    return redirect('liste_fournisseurs')

class ListeAchatsView(LoginRequiredMixin, ListView):
    model = Achat
    template_name = 'liste_achats.html'
    context_object_name = 'achats'
    login_url = 'connexion'
    ordering = ['-date_achat']
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class DetailAchatView(LoginRequiredMixin, DetailView):
    model = Achat
    template_name = 'detail_achat.html'
    context_object_name = 'achat'
    login_url = 'connexion'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lignes'] = self.object.lignes.all()
        return context

class AchatLigneCreateView(LoginRequiredMixin, CreateView):
    model = AchatLigne
    form_class = AchatLigneForm
    template_name = 'ajouter_achat.html'
    success_url = reverse_lazy('liste_achats')

    def form_valid(self, form):
        with transaction.atomic():
            achat_ligne = form.save()
            # Créer automatiquement une entrée dans Stockes
            stock = Stockes.objects.create(
                produit=achat_ligne.produit,
                quantite=achat_ligne.quantite,
                prix_vente=achat_ligne.prix_achat * Decimal('1.2'),  # Marge de 20% par défaut
                stock_minimum=5,  # Valeur par défaut
                achat_ligne=achat_ligne
            )
            # Créer une modification de stock
            ModificationStock.objects.create(
                produit=stock,
                type_modification='ENTREE',
                quantite=achat_ligne.quantite,
                utilisateur=self.request.user,
                raison=f"Nouvel achat - Lot: {achat_ligne.lot}"
            )
        return super().form_valid(form)

@login_required
def ajuster_stock(request, stock_id):
    stock = get_object_or_404(Stockes, id=stock_id)
    if request.method == 'POST':
        nouvelle_quantite = int(request.POST.get('nouvelle_quantite', 0))
        ancienne_quantite = stock.quantite
        difference = nouvelle_quantite - ancienne_quantite
        
        with transaction.atomic():
            stock.quantite = nouvelle_quantite
            stock.save()
            
            # Enregistrer la modification
            type_modif = 'ENTREE' if difference > 0 else 'SORTIE'
            ModificationStock.objects.create(
                produit=stock,
                type_modification=type_modif,
                quantite=abs(difference),
                utilisateur=request.user,
                raison="Ajustement manuel du stock"
            )
            
        messages.success(request, f"Stock ajusté avec succès. Nouvelle quantité : {nouvelle_quantite}")
        return redirect('liste_stock')
    
    return render(request, 'ajuster_stock.html', {'stock': stock})

@login_required
def modifier_stock(request, pk):
    stock = get_object_or_404(Stockes, pk=pk)
    if request.method == 'POST':
        form = StockForm(request.POST, instance=stock)
        if form.is_valid():
            with transaction.atomic():
                previous_quantity = stock.quantite
                modified_stock = form.save()
                quantity_diff = modified_stock.quantite - previous_quantity
                
                if quantity_diff != 0:
                    # Record the stock modification
                    ModificationStock.objects.create(
                        produit=modified_stock,
                        type_modification='AJUSTEMENT',
                        quantite=abs(quantity_diff),
                        utilisateur=request.user,
                        raison=f"Modification du stock {modified_stock.produit.name}"
                    )
            
            messages.success(request, "Stock modifié avec succès !")
            return redirect('liste_stock')
    else:
        form = StockForm(instance=stock)
    
    return render(request, 'modifier_stock.html', {
        'form': form,
        'stock': stock
    })

class DashboardView(LoginRequiredMixin, View):
    template_name = 'dashboard.html'
    
    def get(self, request):
        # Statistiques des stocks
        produits_en_stock = Stockes.objects.all()
        stock_faible = produits_en_stock.filter(quantite__lte=models.F('stock_minimum')).count()
        produits_expires = produits_en_stock.filter(
            achat_ligne__date_expiration__lt=timezone.now().date()
        ).count()
        
        # Statistiques des ventes
        ventes_mois = Vente.objects.filter(
            date_vente__month=timezone.now().month,
            date_vente__year=timezone.now().year
        )
        total_ventes_mois = sum(vente.get_total_amount() for vente in ventes_mois)
        nb_ventes_mois = ventes_mois.count()
        
        # Top 5 des produits les plus vendus
        top_produits = VenteProduit.objects.values(
            'produit__produit__name'
        ).annotate(
            total_vendu=Sum('quantite')
        ).order_by('-total_vendu')[:5]
        
        # Statistiques des achats
        achats_mois = Achat.objects.filter(
            date_achat__month=timezone.now().month,
            date_achat__year=timezone.now().year
        )
        total_achats_mois = sum(
            ligne.prix_achat * ligne.quantite 
            for achat in achats_mois 
            for ligne in achat.lignes.all()
        )
        
        # Calcul de la marge brute du mois
        marge_brute = total_ventes_mois - total_achats_mois
        
        context = {
            'total_produits': produits_en_stock.count(),
            'stock_faible': stock_faible,
            'produits_expires': produits_expires,
            'ventes_mois': nb_ventes_mois,
            'total_ventes_mois': total_ventes_mois,
            'top_produits': top_produits,
            'total_achats_mois': total_achats_mois,
            'marge_brute': marge_brute,
        }
        
        return render(request, self.template_name, context)


