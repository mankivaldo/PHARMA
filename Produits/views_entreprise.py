from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Entreprise, Vente
from .forms_entreprise import EntrepriseForm
from django.contrib.auth.decorators import login_required
from .utils import role_required

@login_required
@role_required('ADMIN', 'GESTIONNAIRE')
def liste_entreprises(request):
    entreprises = Entreprise.objects.all()
    return render(request, 'entreprise/liste_entreprises.html', {'entreprises': entreprises})

@login_required
@role_required('ADMIN', 'GESTIONNAIRE')
def ajouter_entreprise(request):
    if request.method == 'POST':
        form = EntrepriseForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Entreprise ajoutée avec succès!")
            return redirect('liste_entreprises')
    else:
        form = EntrepriseForm()
    return render(request, 'entreprise/ajouter_entreprise.html', {'form': form})

@login_required
@role_required('ADMIN', 'GESTIONNAIRE')
def modifier_entreprise(request, pk):
    entreprise = get_object_or_404(Entreprise, pk=pk)
    if request.method == 'POST':
        form = EntrepriseForm(request.POST, request.FILES, instance=entreprise)
        if form.is_valid():
            form.save()
            messages.success(request, "Entreprise modifiée avec succès!")
            return redirect('liste_entreprises')
    else:
        form = EntrepriseForm(instance=entreprise)
    return render(request, 'entreprise/ajouter_entreprise.html', {'form': form, 'entreprise': entreprise})

@login_required
@role_required('ADMIN', 'GESTIONNAIRE')
def supprimer_entreprise(request, pk):
    entreprise = get_object_or_404(Entreprise, pk=pk)
    if request.method == 'POST':
        entreprise.delete()
        messages.success(request, "Entreprise supprimée avec succès!")
        return redirect('liste_entreprises')
    return redirect('liste_entreprises')

